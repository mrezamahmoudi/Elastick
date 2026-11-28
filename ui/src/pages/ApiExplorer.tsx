import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Alert, Button, Card, Input, Select, Space, Spin, Tag, Typography,
} from 'antd'
import { ApiError, api, getApiKey } from '../api'

const { Text, Paragraph } = Typography
const { TextArea } = Input

const METHOD_COLOR: Record<string, string> = {
  get: 'green',
  post: 'blue',
  put: 'orange',
  delete: 'red',
  head: 'default',
}

interface Operation {
  path: string
  method: string
  summary: string
  description: string
  tag: string
  pathParams: string[]
  queryParams: { name: string; description?: string }[]
  hasBody: boolean
}

export default function ApiExplorer() {
  // The OpenAPI schema of this very service — the source of truth for what
  // can be called. It is public and changes only when the service changes.
  const { data: spec, isLoading, error } = useQuery<any, ApiError>({
    queryKey: ['openapi'],
    queryFn: () => api('/openapi.json'),
    staleTime: Infinity,
  })

  const operations = useMemo<Operation[]>(() => {
    if (!spec?.paths) return []
    const ops: Operation[] = []
    for (const [path, methods] of Object.entries<any>(spec.paths)) {
      for (const [method, op] of Object.entries<any>(methods)) {
        if (!['get', 'post', 'put', 'delete', 'head'].includes(method)) continue
        const params: any[] = op.parameters ?? []
        const declared = params.filter((p) => p.in === 'path').map((p) => p.name)
        const fromBraces = [...path.matchAll(/\{(\w+)\}/g)].map((m) => m[1])
        const pathParams = [...new Set([...declared, ...fromBraces])]
        ops.push({
          path,
          method,
          summary: op.summary ?? '',
          description: op.description ?? '',
          tag: op.tags?.[0] ?? 'default',
          pathParams,
          queryParams: params
            .filter((p) => p.in === 'query')
            .map((p) => ({ name: p.name, description: p.description })),
          hasBody: !!op.requestBody,
        })
      }
    }
    return ops.sort((a, b) => a.path.localeCompare(b.path))
  }, [spec])

  const tags = useMemo(
    () => [...new Set(operations.map((o) => o.tag))].sort(),
    [operations],
  )

  const [tag, setTag] = useState<string>('Diagnostics')
  const [selected, setSelected] = useState<Operation | null>(null)
  const [pathValues, setPathValues] = useState<Record<string, string>>({})
  const [queryValues, setQueryValues] = useState<Record<string, string>>({})
  const [bodyText, setBodyText] = useState('')
  const [status, setStatus] = useState<number | null>(null)
  const [response, setResponse] = useState<string>('')
  const [sending, setSending] = useState(false)

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '80px auto' }} />
  if (error) return <Alert type="error" showIcon message={`Failed to load API schema: ${error.message}`} />

  const visible = operations.filter((o) => o.tag === tag)

  function selectOperation(op: Operation) {
    setSelected(op)
    setPathValues({})
    setQueryValues({})
    setBodyText('')
    setStatus(null)
    setResponse('')
  }

  async function execute() {
    if (!selected) return
    let url = selected.path
    for (const p of selected.pathParams) {
      url = url.replace(`{${p}}`, encodeURIComponent(pathValues[p] ?? ''))
    }
    const qs = new URLSearchParams()
    for (const q of selected.queryParams) {
      const v = queryValues[q.name]
      if (v) qs.append(q.name, v)
    }
    if ([...qs.keys()].length > 0) url += `?${qs.toString()}`

    const headers: Record<string, string> = {}
    const key = getApiKey()
    if (key) headers['X-API-Key'] = key
    const body = selected.hasBody && bodyText.trim() ? bodyText : undefined
    if (body) headers['Content-Type'] = 'application/json'

    setSending(true)
    setStatus(null)
    setResponse('')
    try {
      const res = await fetch(url, { method: selected.method.toUpperCase(), headers, body })
      setStatus(res.status)
      const text = await res.text()
      try {
        setResponse(JSON.stringify(JSON.parse(text), null, 2))
      } catch {
        setResponse(text || '(empty response)')
      }
    } catch (e: any) {
      setStatus(0)
      setResponse(String(e))
    } finally {
      setSending(false)
    }
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card size="small" title="API Explorer">
        <Space wrap>
          <Text>Category:</Text>
          <Select
            style={{ width: 280 }}
            value={tag}
            onChange={(v) => { setTag(v); setSelected(null) }}
            options={tags.map((t) => ({ value: t, label: t }))}
            showSearch
          />
          <Text type="secondary">
            Every endpoint of this service, generated live from openapi.json —
            {operations.length} operations in {tags.length} categories.
          </Text>
        </Space>
      </Card>

      <Card size="small" title={`Endpoints in “${tag}” (${visible.length})`}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {visible.map((op) => (
            <div
              key={`${op.method} ${op.path}`}
              onClick={() => selectOperation(op)}
              style={{
                padding: '6px 10px', cursor: 'pointer', borderRadius: 6,
                background:
                  selected?.method === op.method && selected?.path === op.path
                    ? '#e6f4ff' : undefined,
              }}
            >
              <Space wrap>
                <Tag color={METHOD_COLOR[op.method]} style={{ minWidth: 64, textAlign: 'center' }}>
                  {op.method.toUpperCase()}
                </Tag>
                <Text code>{op.path}</Text>
                <Text type="secondary">{op.summary}</Text>
              </Space>
            </div>
          ))}
        </Space>
      </Card>

      {selected && (
        <Card
          size="small"
          title={
            <Space wrap>
              <Tag color={METHOD_COLOR[selected.method]}>{selected.method.toUpperCase()}</Tag>
              <Text code>{selected.path}</Text>
            </Space>
          }
          extra={
            <Button type="primary" loading={sending} onClick={execute}>
              Send
            </Button>
          }
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {selected.description && (
              <Paragraph type="secondary" style={{ whiteSpace: 'pre-wrap', marginBottom: 0 }}>
                {selected.description}
              </Paragraph>
            )}

            {selected.pathParams.length > 0 && (
              <div>
                <Text strong>Path parameters</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {selected.pathParams.map((p) => (
                    <Input
                      key={p}
                      addonBefore={`{${p}}`}
                      placeholder={`value for ${p}`}
                      value={pathValues[p] ?? ''}
                      onChange={(e) => setPathValues({ ...pathValues, [p]: e.target.value })}
                    />
                  ))}
                </Space>
              </div>
            )}

            {selected.queryParams.length > 0 && (
              <div>
                <Text strong>Query parameters (optional)</Text>
                <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                  {selected.queryParams.map((q) => (
                    <Input
                      key={q.name}
                      addonBefore={q.name}
                      placeholder={q.description ?? 'leave empty to omit'}
                      value={queryValues[q.name] ?? ''}
                      onChange={(e) => setQueryValues({ ...queryValues, [q.name]: e.target.value })}
                    />
                  ))}
                </Space>
              </div>
            )}

            {selected.hasBody && (
              <div>
                <Text strong>Request body (JSON)</Text>
                <TextArea
                  rows={6}
                  style={{ marginTop: 8, fontFamily: 'monospace' }}
                  placeholder='{"query": {"match_all": {}}}'
                  value={bodyText}
                  onChange={(e) => setBodyText(e.target.value)}
                />
              </div>
            )}

            {status !== null && (
              <div>
                <Space>
                  <Text strong>Response</Text>
                  <Tag color={status >= 200 && status < 300 ? 'green' : 'red'}>
                    {status === 0 ? 'network error' : status}
                  </Tag>
                </Space>
                <pre
                  style={{
                    maxHeight: 420, overflow: 'auto', fontSize: 12,
                    background: '#fafafa', padding: 12, border: '1px solid #eee',
                  }}
                >
                  {response}
                </pre>
              </div>
            )}
          </Space>
        </Card>
      )}
    </Space>
  )
}
