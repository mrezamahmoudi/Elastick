import { useEffect, useState } from 'react'
import {
  Layout, Menu, Button, Modal, Input, Space, Typography, Alert,
} from 'antd'
import {
  DashboardOutlined, DatabaseOutlined, ClusterOutlined,
  ApiOutlined, KeyOutlined, NodeIndexOutlined,
} from '@ant-design/icons'
import { getApiKey, setApiKey } from './api'
import Overview from './pages/Overview'
import Indices from './pages/Indices'
import Shards from './pages/Shards'
import ApiExplorer from './pages/ApiExplorer'

const { Sider, Content, Header } = Layout
const { Text } = Typography

type PageKey = 'overview' | 'indices' | 'shards' | 'explorer'

const PAGES: Record<PageKey, { label: string; icon: JSX.Element; node: () => JSX.Element }> = {
  overview: { label: 'Overview', icon: <DashboardOutlined />, node: () => <Overview /> },
  indices: { label: 'Indices', icon: <DatabaseOutlined />, node: () => <Indices /> },
  shards: { label: 'Shards', icon: <ClusterOutlined />, node: () => <Shards /> },
  explorer: { label: 'API Explorer', icon: <NodeIndexOutlined />, node: () => <ApiExplorer /> },
}

export default function App() {
  const [page, setPage] = useState<PageKey>('overview')
  const [keyModalOpen, setKeyModalOpen] = useState(false)
  const [keyDraft, setKeyDraft] = useState('')

  // Any 401 from the backend opens the API-key prompt.
  useEffect(() => {
    const onUnauthorized = () => {
      setKeyDraft(getApiKey())
      setKeyModalOpen(true)
    }
    window.addEventListener('elastick:unauthorized', onUnauthorized)
    return () => window.removeEventListener('elastick:unauthorized', onUnauthorized)
  }, [])

  const current = PAGES[page]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={200}>
        <div style={{ color: '#fff', fontWeight: 700, fontSize: 18, padding: '16px 24px' }}>
          🧵 Elastick
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[page]}
          onClick={(e) => setPage(e.key as PageKey)}
          items={Object.entries(PAGES).map(([key, p]) => ({
            key,
            icon: p.icon,
            label: p.label,
          }))}
        />
        <div style={{ position: 'absolute', bottom: 16, width: '100%', padding: '0 16px' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button block icon={<KeyOutlined />} onClick={() => { setKeyDraft(getApiKey()); setKeyModalOpen(true) }}>
              API key
            </Button>
            <Button block icon={<ApiOutlined />} href="/docs" target="_blank">
              Swagger
            </Button>
          </Space>
        </div>
      </Sider>

      <Layout>
        <Header style={{ background: '#fff', borderBottom: '1px solid #f0f0f0', padding: '0 24px' }}>
          <Space>
            <Text strong style={{ fontSize: 16 }}>{current.label}</Text>
            <Text type="secondary">live view of your Elasticsearch cluster</Text>
          </Space>
        </Header>
        <Content style={{ padding: 24, background: '#f5f5f5' }}>
          {current.node()}
        </Content>
      </Layout>

      <Modal
        title="Elastick API key"
        open={keyModalOpen}
        onCancel={() => setKeyModalOpen(false)}
        footer={null}
      >
        <Alert
          style={{ marginBottom: 16 }}
          type="info"
          showIcon
          message="Leave empty if the service runs without ELASTICK_API_KEY."
        />
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="X-API-Key"
            value={keyDraft}
            onChange={(e) => setKeyDraft(e.target.value)}
            onPressEnter={() => { setApiKey(keyDraft.trim()); setKeyModalOpen(false) }}
          />
          <Button type="primary" onClick={() => { setApiKey(keyDraft.trim()); setKeyModalOpen(false) }}>
            Save
          </Button>
        </Space.Compact>
      </Modal>
    </Layout>
  )
}
