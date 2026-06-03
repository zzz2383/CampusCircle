import request from './request'

/**
 * 上传图片
 * @param file 图片文件
 * @returns 上传后的 URL 和文件名
 */
export async function uploadImage(file: File): Promise<{ url: string; filename: string }> {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/upload/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }) as any
}
