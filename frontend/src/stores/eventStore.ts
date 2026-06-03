import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getEvents, getEventById, createEvent, updateEvent, deleteEvent, registerEvent, cancelRegister, getParticipants } from '@/services/event'
import type { Event, CreateEventPayload, UpdateEventPayload, EventParticipant } from '@/types'

export const useEventStore = defineStore('event', () => {
    const events = ref<Event[]>([])
    const total = ref(0)
    const loading = ref(false)
    const currentEvent = ref<Event | null>(null)
    const participants = ref<EventParticipant[]>([])
    const participantsLoading = ref(false)
    const offset = ref(0)
    const limit = 20
    const hasMore = ref(false)

    const fetchEvents = async (reset = true, clubId?: number) => {
        if (loading.value) return
        loading.value = true
        try {
            const params: any = {
                offset: reset ? 0 : offset.value,
                limit,
            }
            if (clubId) params.club_id = clubId

            const res = await getEvents(params)
            if (reset) {
                events.value = res.items
                offset.value = res.items.length
            } else {
                events.value.push(...res.items)
                offset.value += res.items.length
            }
            total.value = res.total
            hasMore.value = events.value.length < res.total
        } catch (error) {
            console.error('fetchEvents failed', error)
        } finally {
            loading.value = false
        }
    }

    const loadMore = () => {
        if (!hasMore.value || loading.value) return
        fetchEvents(false)
    }

    const fetchEventDetail = async (eventId: number) => {
        loading.value = true
        try {
            const event = await getEventById(eventId)
            currentEvent.value = event
            await fetchParticipants(eventId)
            return event
        } finally {
            loading.value = false
        }
    }

    const fetchParticipants = async (eventId: number) => {
        participantsLoading.value = true
        try {
            const data = await getParticipants(eventId)
            participants.value = data
        } finally {
            participantsLoading.value = false
        }
    }

    const createNewEvent = async (data: CreateEventPayload) => {
        const newEvent = await createEvent(data)
        events.value.unshift(newEvent)
        total.value++
        return newEvent
    }

    const updateExistingEvent = async (eventId: number, data: UpdateEventPayload) => {
        const updated = await updateEvent(eventId, data)
        const index = events.value.findIndex(e => e.id === eventId)
        if (index !== -1) events.value[index] = updated
        if (currentEvent.value?.id === eventId) currentEvent.value = updated
        return updated
    }

    const deleteExistingEvent = async (eventId: number) => {
        await deleteEvent(eventId)
        events.value = events.value.filter(e => e.id !== eventId)
        total.value--
        if (currentEvent.value?.id === eventId) currentEvent.value = null
    }

    const registerForEvent = async (eventId: number) => {
        await registerEvent(eventId)
        // 更新本地状态
        const event = events.value.find(e => e.id === eventId)
        if (event) {
            event.participant_count++
            event.is_registered = true
        }
        if (currentEvent.value?.id === eventId) {
            currentEvent.value.participant_count++
            currentEvent.value.is_registered = true
        }
        await fetchParticipants(eventId)
    }

    const cancelRegistration = async (eventId: number) => {
        await cancelRegister(eventId)
        const event = events.value.find(e => e.id === eventId)
        if (event) {
            event.participant_count--
            event.is_registered = false
        }
        if (currentEvent.value?.id === eventId) {
            currentEvent.value.participant_count--
            currentEvent.value.is_registered = false
        }
        await fetchParticipants(eventId)
    }

    return {
        events,
        total,
        loading,
        hasMore,
        currentEvent,
        participants,
        participantsLoading,
        fetchEvents,
        loadMore,
        fetchEventDetail,
        createNewEvent,
        updateExistingEvent,
        deleteExistingEvent,
        registerForEvent,
        cancelRegistration,
    }
})