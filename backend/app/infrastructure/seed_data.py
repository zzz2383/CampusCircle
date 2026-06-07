"""
功能：数据库种子数据（演示用初始数据）

实现逻辑：
    1. 在 init_db() 建表后调用，插入演示数据
    2. 先检查用户总数，若已有数据则跳过（幂等）
    3. 依次插入：用户 → 社团 → 社团成员 → 帖子 → 评论 → 活动 → 失物招领

调用链路：
    - 被 app/infrastructure/db.py 中的 init_db() 调用
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import async_session_factory
from app.infrastructure.logger import get_logger
from app.business.impl.auth_utils import hash_password
from app.models.domain import User, Club, ClubMember, Post, Comment, Event, EventParticipant, LostItem
from app.models.enums import UserRole, Gender

logger = get_logger(__name__)


async def seed_demo_data():
    """种子数据：插入演示用的用户、社团、帖子、评论和活动

    实现逻辑：
        1. 检查用户表是否已有超过 1 条记录（仅管理员 = 未初始化）
        2. 若已初始化则跳过，否则插入全套演示数据
        3. 所有数据通过同一次会话提交，保证原子性

    测试用例：
        - test_seed_demo_data_created
        - test_seed_demo_data_idempotent
    """
    async with async_session_factory() as session:
        try:
            # ── 检查是否已有种子数据 ──
            count_result = await session.execute(select(func.count()).select_from(User))
            user_count = count_result.scalar()
            if user_count and user_count > 1:
                logger.info("Demo data already exists, skipping seed")
                return

            logger.info("Seeding demo data...")

            # ── 1. 创建演示用户 ──
            users = _create_users()
            session.add_all(users)
            await session.flush()
            user_map = {u.student_id: u for u in users}

            # ── 2. 创建社团 ──
            clubs = _create_clubs()
            session.add_all(clubs)
            await session.flush()
            club_map = {c.name: c for c in clubs}

            # ── 3. 添加社团成员 ──
            members = _create_club_members(user_map, club_map)
            session.add_all(members)

            # ── 4. 创建帖子 ──
            posts = _create_posts(user_map, club_map)
            session.add_all(posts)
            await session.flush()

            # ── 5. 创建评论 ──
            comments = _create_comments(user_map, posts)
            session.add_all(comments)

            # ── 6. 创建活动 ──
            events = _create_events(club_map)
            session.add_all(events)

            # ── 7. 创建失物招领 ──
            lost_items = _create_lost_items(user_map)
            session.add_all(lost_items)

            await session.commit()
            logger.info(
                f"Demo data seeded: {len(users)} users, {len(clubs)} clubs, "
                f"{len(posts)} posts, {len(comments)} comments, {len(events)} events"
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to seed demo data: {e}")
            raise
        finally:
            await session.close()


# ══════════════════════════════════════════════
#  数据构建函数（纯同步，不涉及数据库操作）
# ══════════════════════════════════════════════

def _create_users() -> list[User]:
    """创建 4 个演示用户"""
    now = datetime.now(timezone.utc)
    return [
        User(
            student_id="2024001",
            email="zhangsan@campus.edu",
            nickname="张三",
            password_hash=hash_password("pass123"),
            role=UserRole.STUDENT,
            gender=Gender.MALE,
            department="计算机科学",
            grade="2023",
            is_active=True,
            created_at=now,
        ),
        User(
            student_id="2024002",
            email="lisi@campus.edu",
            nickname="李四",
            password_hash=hash_password("pass123"),
            role=UserRole.STUDENT,
            gender=Gender.MALE,
            department="数学系",
            grade="2022",
            is_active=True,
            created_at=now,
        ),
        User(
            student_id="T2024001",
            email="wanglaoshi@campus.edu",
            nickname="王老师",
            password_hash=hash_password("pass123"),
            role=UserRole.TEACHER,
            gender=Gender.FEMALE,
            department="计算机科学",
            grade=None,
            is_active=True,
            created_at=now,
        ),
        User(
            student_id="2024003",
            email="zhaoliu@campus.edu",
            nickname="赵六",
            password_hash=hash_password("pass123"),
            role=UserRole.STUDENT,
            gender=Gender.OTHER,
            department="英语系",
            grade="2024",
            is_active=True,
            created_at=now,
        ),
    ]


def _create_clubs() -> list[Club]:
    """创建 3 个演示社团"""
    now = datetime.now(timezone.utc)
    return [
        Club(
            name="计算机协会",
            description="计算机科学与技术爱好者的聚集地，定期举办编程比赛、技术讲座和项目实践。",
            created_at=now,
        ),
        Club(
            name="数学社",
            description="数学爱好者的交流平台，涵盖高等数学、线性代数、概率论等学科讨论。",
            created_at=now,
        ),
        Club(
            name="英语角",
            description="英语学习与交流的乐园，每周举办英语沙龙、四六级备考分享和观影活动。",
            created_at=now,
        ),
    ]


def _create_club_members(
    user_map: dict[str, User],
    club_map: dict[str, Club],
) -> list[ClubMember]:
    """创建社团成员关系"""
    now = datetime.now(timezone.utc)
    return [
        ClubMember(user_id=user_map["2024001"].id, club_id=club_map["计算机协会"].id, role="admin", joined_at=now),
        ClubMember(user_id=user_map["T2024001"].id, club_id=club_map["计算机协会"].id, role="member", joined_at=now),
        ClubMember(user_id=user_map["2024002"].id, club_id=club_map["数学社"].id, role="admin", joined_at=now),
        ClubMember(user_id=user_map["2024003"].id, club_id=club_map["英语角"].id, role="admin", joined_at=now),
    ]


def _create_posts(
    user_map: dict[str, User],
    club_map: dict[str, Club],
) -> list[Post]:
    """创建 6 篇演示帖子"""
    now = datetime.now(timezone.utc)
    return [
        Post(
            user_id=user_map["2024001"].id,
            title="计算机协会2024秋季招新啦！",
            content="""欢迎各位同学加入计算机协会！🎉

在这里你可以：
- 参加编程比赛（ACM、蓝桥杯）
- 聆听技术大牛讲座
- 参与开源项目实战
- 认识志同道合的朋友

招新时间：9月10日-9月20日
地点：大学生活动中心三楼

无需基础，只要你有热情！""",
            tags="社团,活动",
            club_id=club_map["计算机协会"].id,
            view_count=128,
            is_active=True,
            created_at=now - timedelta(hours=2),
        ),
        Post(
            user_id=user_map["2024002"].id,
            title="求助：高等数学数列极限怎么理解？",
            content="""刚上大一，高数课上讲到数列极限的 ε-N 定义，感觉很抽象。

有没有学长学姐分享下学习经验？怎么才能更好地理解这个概念？
有没有推荐的练习题和资源？在线等，挺急的 😭""",
            tags="求助,课程",
            view_count=56,
            is_active=True,
            created_at=now - timedelta(hours=5),
        ),
        Post(
            user_id=user_map["T2024001"].id,
            title="【通知】计算机科学专业讲座：人工智能前沿进展",
            content="""讲座主题：大语言模型时代的机遇与挑战

主讲人：张教授（清华大学计算机系）
时间：本周五下午 14:00-16:00
地点：教学楼A座101报告厅

欢迎全校师生参加！座位有限，请提前入场。""",
            tags="通知,讲座,活动",
            view_count=200,
            is_active=True,
            created_at=now - timedelta(hours=8),
        ),
        Post(
            user_id=user_map["2024003"].id,
            title="英语四级600分备考经验分享",
            content="""四级考了602分，分享一下我的备考经验：

📚 听力：每天听30分钟 VOA/BBC，精听+泛听结合
📚 阅读：真题为主，每天2篇仔细阅读+1篇长篇阅读
📚 写作：背诵模板但不要死套，积累高级表达
📚 翻译：关注中国文化类词汇

推荐资料：
1. 华研外语四级真题
2. 百词斩App背单词
3. 可可英语听力

祝大家四级高分通过！💪""",
            tags="课程,社团",
            club_id=club_map["英语角"].id,
            view_count=89,
            is_active=True,
            created_at=now - timedelta(hours=12),
        ),
        Post(
            user_id=user_map["2024001"].id,
            title="失物招领：二食堂捡到蓝色保温杯",
            content="""今天中午在二食堂一楼靠窗位置捡到一个蓝色保温杯（上面有 Starbucks 标志）。

请失主联系我：
- 手机：138xxxx8901
- 宿舍：7号楼302

也请大家帮忙转发，谢谢！""",
            tags="失物招领",
            view_count=35,
            is_active=True,
            created_at=now - timedelta(hours=3),
        ),
        Post(
            user_id=user_map["2024002"].id,
            title="周末羽毛球活动报名",
            content="""这周六下午组织羽毛球活动，欢迎报名！

🕒 时间：周六 15:00-18:00
📍 地点：体育馆羽毛球馆
💰 费用：AA制（约15元/人）
🏸 球拍自备，我们提供羽毛球

报名请回复本贴或私信我！""",
            tags="活动,社团",
            club_id=club_map["数学社"].id,
            view_count=72,
            is_active=True,
            created_at=now - timedelta(hours=6),
        ),
    ]


def _create_comments(
    user_map: dict[str, User],
    posts: list[Post],
) -> list[Comment]:
    """创建 5 条演示评论"""
    now = datetime.now(timezone.utc)
    post_map = {p.title: p for p in posts}
    return [
        Comment(
            post_id=post_map["计算机协会2024秋季招新啦！"].id,
            user_id=user_map["2024002"].id,
            content="请问非计算机专业的可以加入吗？",
            is_active=True,
            created_at=now - timedelta(hours=1),
        ),
        Comment(
            post_id=post_map["计算机协会2024秋季招新啦！"].id,
            user_id=user_map["2024001"].id,
            content="当然可以！我们欢迎所有专业的同学 😊",
            is_active=True,
            created_at=now - timedelta(minutes=50),
        ),
        Comment(
            post_id=post_map["求助：高等数学数列极限怎么理解？"].id,
            user_id=user_map["T2024001"].id,
            content='建议先看教材上的几何解释，ε 可以理解为"误差范围"，N 是"从第几项开始"。结合图像理解会容易很多。',
            is_active=True,
            created_at=now - timedelta(hours=4),
        ),
        Comment(
            post_id=post_map["英语四级600分备考经验分享"].id,
            user_id=user_map["2024001"].id,
            content="好厉害！求推荐好用的背单词App 📱",
            is_active=True,
            created_at=now - timedelta(hours=10),
        ),
        Comment(
            post_id=post_map["周末羽毛球活动报名"].id,
            user_id=user_map["2024003"].id,
            content="报名+1！需要带拍子吗？",
            is_active=True,
            created_at=now - timedelta(hours=5),
        ),
    ]


def _create_events(club_map: dict[str, Club]) -> list[Event]:
    """创建 2 个演示活动"""
    now = datetime.now(timezone.utc)
    return [
        Event(
            club_id=club_map["计算机协会"].id,
            title="Python 入门工作坊",
            description="面向零基础同学的 Python 编程入门活动，涵盖基础语法、爬虫入门和小项目实战。请自带笔记本电脑。",
            location="教学楼B座302机房",
            max_participants=30,
            start_time=now + timedelta(days=3, hours=14),
            end_time=now + timedelta(days=3, hours=17),
            created_at=now,
        ),
        Event(
            club_id=club_map["英语角"].id,
            title="英语角：Travel Around the World",
            description="本期话题：旅行。用英语分享你的旅行经历或梦想的目的地。外教 Mark 也会参与！",
            location="大学生活动中心二楼咖啡厅",
            max_participants=20,
            start_time=now + timedelta(days=5, hours=15),
            end_time=now + timedelta(days=5, hours=17),
            created_at=now,
        ),
    ]


def _create_lost_items(user_map: dict[str, User]) -> list[LostItem]:
    """创建 1 条失物招领"""
    now = datetime.now(timezone.utc)
    return [
        LostItem(
            user_id=user_map["2024003"].id,
            title="学生证丢失",
            description="下午在图书馆丢失学生证一枚，姓名赵六，学号2024003。捡到的同学请联系我，万分感谢！",
            location="图书馆三楼自习区",
            contact="手机：139xxxx4567",
            is_lost=True,
            is_found=False,
            expires_at=now + timedelta(days=7),
            created_at=now,
        ),
    ]
