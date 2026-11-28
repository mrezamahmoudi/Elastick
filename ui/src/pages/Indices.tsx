import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Alert, Card, Input, Space, Table, Tag } from 'antd'
import { ApiError, api } from '../api'

const STATUS_COLOR: Record<string, string> = {
  green: 'green',
  yellow: 'orange',
  red: 'red',
}

export default function Indices() {
  const [search, setSearch] = useState('')

  // Backed by the curated `GET /indices` endpoint (the _cat/indices view).
  const { data, isLoading, error } = useQuery<any[], ApiError>({
    queryKey: ['indices'],
    queryFn: () => api('/indices'),
    refetchInterval: 30000,
  })

  const rows = (data ?? []).filter((r: any) =>
    (r.index ?? '').toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    {
      title: 'Health', dataIndex: 'health', key: 'health', width: 100,
      render: (v: string) => <Tag color={STATUS_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 100 },
    { title: 'Index', dataIndex: 'index', key: 'index' },
    { title: 'Docs', dataIndex: ['docs.count'], key: 'docs', render: (v: any) => v ?? '–' },
    { title: 'Store size', dataIndex: ['store.size'], key: 'store', render: (v: any) => v ?? '–' },
    { title: 'Pri', dataIndex: 'pri', key: 'pri', width: 70 },
    { title: 'Rep', dataIndex: 'rep', key: 'rep', width: 70 },
  ]

  if (error) return <Alert type="error" showIcon message={`Failed to load indices: ${error.message}`} />

  return (
    <Card
      title="Indices"
      size="small"
      extra={
        <Space>
          <Input.Search
            placeholder="Filter by name…"
            allowClear
            style={{ width: 260 }}
            onSearch={setSearch}
            onChange={(e) => !e.target.value && setSearch('')}
          />
        </Space>
      }
    >
      <Table
        size="small"
        rowKey={(r: any) => r.uuid ?? r.index}
        loading={isLoading}
        dataSource={rows}
        columns={columns}
        pagination={{ pageSize: 25, showSizeChanger: true }}
      />
    </Card>
  )
}
