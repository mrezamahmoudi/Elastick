import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Alert, Button, Card, Modal, Space, Table, Tag, Typography,
} from 'antd'
import { ApiError, api } from '../api'

const { Text } = Typography

export default function Shards() {
  const [explain, setExplain] = useState<any | null>(null)

  // Backed by the curated `GET /shards/unassigned` endpoint.
  const { data, isLoading, error } = useQuery<any[], ApiError>({
    queryKey: ['unassigned-shards'],
    queryFn: () => api('/shards/unassigned'),
    refetchInterval: 20000,
  })

  // POST /shards/allocation-explain — ask ES why this shard is not placed.
  const explainMutation = useMutation<any, ApiError, any>({
    mutationFn: (shard: any) =>
      api('/shards/allocation-explain', {
        method: 'POST',
        body: JSON.stringify({
          index: shard.index,
          shard: Number(shard.shard),
          primary: String(shard.prirep ?? '').toLowerCase().startsWith('p'),
        }),
      }),
    onSuccess: (result) => setExplain(result),
  })

  const columns = [
    { title: 'Index', dataIndex: 'index', key: 'index' },
    { title: 'Shard', dataIndex: 'shard', key: 'shard', width: 80 },
    {
      title: 'Type', dataIndex: 'prirep', key: 'prirep', width: 90,
      render: (v: string) => (
        <Tag color={String(v).toLowerCase().startsWith('p') ? 'blue' : 'purple'}>
          {String(v).toLowerCase().startsWith('p') ? 'primary' : 'replica'}
        </Tag>
      ),
    },
    {
      title: 'Reason', dataIndex: 'unassign.reason', key: 'reason', width: 140,
      render: (v: string) => <Tag>{v || 'unknown'}</Tag>,
    },
    {
      title: '', key: 'actions', width: 120,
      render: (_: unknown, row: any) => (
        <Button
          size="small"
          loading={explainMutation.isPending && explainMutation.variables === row}
          onClick={() => explainMutation.mutate(row)}
        >
          Explain
        </Button>
      ),
    },
  ]

  if (error) return <Alert type="error" showIcon message={`Failed to load shards: ${error.message}`} />

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {(data ?? []).length === 0 && !isLoading ? (
        <Alert type="success" showIcon message="No unassigned shards — every shard is placed." />
      ) : (
        <Card title={`Unassigned shards (${(data ?? []).length})`} size="small">
          <Table
            size="small"
            rowKey={(r: any) => `${r.index}-${r.shard}-${r.prirep}`}
            loading={isLoading}
            dataSource={data}
            columns={columns}
            pagination={false}
          />
        </Card>
      )}

      <Modal
        title="Allocation explain"
        open={explain !== null}
        onCancel={() => setExplain(null)}
        footer={null}
        width={720}
      >
        {explain && (
          <pre style={{ maxHeight: 480, overflow: 'auto', fontSize: 12, background: '#fafafa', padding: 12 }}>
            {JSON.stringify(explain, null, 2)}
          </pre>
        )}
      </Modal>
    </Space>
  )
}
