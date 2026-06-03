import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getClubs, getClubById, createClub, joinClub, leaveClub, getClubMembers, checkIsMember, getClubPosts, getClubEvents } from '@/services/club'
import type { Club, ClubMember, PostDTO, EventDTO } from '@/types'

export const useClubStore = defineStore('club', () => {
    const clubs = ref<Club[]>([])
    const currentClub = ref<Club | null>(null)
    const members = ref<ClubMember[]>([])
    const posts = ref<PostDTO[]>([])
    const events = ref<EventDTO[]>([])
    const isMember = ref(false)
    const loading = ref(false)

    const fetchClubs = async () => {
        loading.value = true
        try {
            const data = await getClubs()
            clubs.value = data
        } finally {
            loading.value = false
        }
    }

    const fetchClubDetail = async (clubId: number) => {
        loading.value = true
        try {
            const club = await getClubById(clubId)
            currentClub.value = club
            // 并行获取成员、帖子、活动
            const [membersData, memberStatus, postsData, eventsData] = await Promise.all([
                getClubMembers(clubId),
                checkIsMember(clubId),
                getClubPosts(clubId, { offset: 0, limit: 20 }),
                getClubEvents(clubId, { offset: 0, limit: 20 })
            ])
            members.value = membersData
            isMember.value = memberStatus.is_member
            posts.value = postsData.items
            events.value = eventsData
        } finally {
            loading.value = false
        }
    }

    const createNewClub = async (data: { name: string; description?: string }) => {
        const newClub = await createClub(data)
        clubs.value.unshift(newClub)
        return newClub
    }

    const joinClubAction = async (clubId: number) => {
        await joinClub(clubId)
        isMember.value = true
        // 可选：重新获取成员列表
        const newMembers = await getClubMembers(clubId)
        members.value = newMembers
    }

    const leaveClubAction = async (clubId: number) => {
        await leaveClub(clubId)
        isMember.value = false
        const newMembers = await getClubMembers(clubId)
        members.value = newMembers
    }

    return {
        clubs,
        currentClub,
        members,
        posts,
        events,
        isMember,
        loading,
        fetchClubs,
        fetchClubDetail,
        createNewClub,
        joinClubAction,
        leaveClubAction,
    }
})