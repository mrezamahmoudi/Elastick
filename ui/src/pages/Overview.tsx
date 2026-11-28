import { useQuery } from '@tanstack/react-query'
import {
  Alert, Card, Col, Row, Space, Statistic, Table, Tag, Typography, Spin,
} from 'antd'
import { ApiError, api } from '../api'

const { Text } = Typography

const STATUS_COLOR: Record<string, string> = {
  green: 'green',
  yellow: 'orange',
  red: 'red',
}

export default function Overview() {
  // Polls the curated overview report every 15s — the one-call health check.
  const { data, isLoading, error } = useQuery<any, ApiError>({
    queryKey: ['overview'],
    queryFn: () => api('/diagnostics/overview'),
    refetchInterval: 15000,
  })

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '80px auto' }} />
  if (error) return <Alert type="error" showIcon message={`Failed to load overview: ${error.message}`} />
  if (!data) return null

  const health = data.health ?? {}
  const nodes: any[] = data.nodes ?? []
  const disk: any[] = data.disk ?? []
  const problems: string[] = data.problems ?? []
  const nonGreen: any[] = data.non_green_indices ?? []

  const nodeColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Version', dataIndex: 'version', key: 'version' },
    {
      title: 'Roles', dataIndex: 'roles', key: 'roles',
      render: (roles: string[]) => (roles ?? []).map((r) => <Tag key={r}>{r}</Tag>),
    },
  ]

  const diskColumns = [
    { title: 'Node', dataIndex: 'node', key: 'node' },
    { title: 'Shards', dataIndex: 'shards', key: 'shards' },
    {
      title: 'Disk used', dataIndex: 'disk.percent', key: 'disk.percent',
      render: (_: unknown, row: any) => {
        const pct = parseInt(String(row['disk.percent'] ?? '0').replace('%', ''), 10)
        const color = pct >= 90 ? 'red' : pct >= 85 ? 'orange' : 'green'
        return <Tag color={color}>{row['disk.percent']}</Tag>
      },
    },
  ]

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>

      <Card>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="Cluster status"
              value={(health.status ?? 'unknown').toUpperCase()}
              valueStyle={{
                color: health.status === 'red' ? '#cf1322'
                  : health.status === 'yellow' ? '#d46b08'
                  : health.status === 'green' ? '#389e0d' : undefined,
                fontSize: 24,
              }}
            />
          </Col>
          <Col span={4}><Statistic title="Nodes" value={health.number_of_nodes ?? '–'} /></Col>
          <Col span={4}><Statistic title="Active shards" value={health.active_shards ?? '–'} /></Col>
          <Col span={5}>
            <Statistic
              title="Unassigned shards"
              value={health.unassigned_shards ?? 0}
              valueStyle={{ color: (health.unassigned_shards ?? 0) > 0 ? '#cf1322' : undefined }}
            />
          </Col>
          <Col span={5}>
            <Statistic
              title="Non-green indices"
              value={nonGreen.length}
              valueStyle={{ color: nonGreen.length > 0 ? '#fa8c16' : undefined }}
            />
          </Col>
        </Row>
      </Card>

      {problems.length > 0 ? (
        problems.map((p, i) => <Alert key={i} type="warning" showIcon message={p} />)
      ) : (
        <Alert type="success" showIcon message="No problems detected — the cluster looks healthy." />
      )}

      <Card title="Nodes" size="small">
        <Table
          size="small"
          rowKey="name"
          loading={isLoading}
          dataSource={nodes}
          columns={nodeColumns}
          pagination={false}
        />
      </Card>

      <Card title="Disk allocation per node" size="small">
        <Table
          size="small"
          rowKey="node"
          loading={isLoading}
          dataSource={disk}
          columns={diskColumns}
          pagination={false}
        />
      </Card>

      {nonGreen.length > 0 && (
        <Card title="Indices that are not green" size="small">
          {nonGreen.map((n: any) => (
            <Text key={n.index}>
              <Tag color={STATUS_COLOR[n.status] ?? 'default'}>{n.status}</Tag>
              {n.index}
              <br />
            </Text>
          ))}
        </Card>
      )}
    </Space>
  )
}
