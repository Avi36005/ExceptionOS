export interface NotificationItem {
  id: string
  organization_id: string
  user_id: string
  notification_type: string
  title: string
  body?: string | null
  link?: string | null
  related_case_id?: string | null
  read: boolean
  read_at?: string | null
  created_at: string
  [key: string]: unknown
}
