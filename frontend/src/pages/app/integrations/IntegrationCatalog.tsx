import { useNavigate } from 'react-router-dom'
import { Plug, CheckCircle, ExternalLink } from 'lucide-react'

const integrations = [
  { id: 'openclaw', name: 'OpenClaw', category: 'Legal AI', desc: 'AI-powered legal document analysis and contract review integration.', connected: false, featured: true },
  { id: 'slack', name: 'Slack', category: 'Communication', desc: 'Send exception notifications and approvals directly in Slack channels.', connected: true, featured: false },
  { id: 'jira', name: 'Jira', category: 'Project Management', desc: 'Sync exceptions with Jira tickets and track implementation of approved changes.', connected: false, featured: false },
  { id: 'okta', name: 'Okta', category: 'Identity', desc: 'SSO and user provisioning via Okta for enterprise organizations.', connected: true, featured: false },
  { id: 'salesforce', name: 'Salesforce', category: 'CRM', desc: 'Link exceptions to Salesforce opportunities and account records.', connected: false, featured: false },
  { id: 'servicenow', name: 'ServiceNow', category: 'ITSM', desc: 'Bi-directional sync with ServiceNow IT service management workflows.', connected: false, featured: false },
  { id: 'webhook', name: 'Webhooks', category: 'Custom', desc: 'Send events to any endpoint via customizable webhooks.', connected: true, featured: false },
  { id: 'api', name: 'REST API', category: 'Developer', desc: 'Full REST API access for custom integrations and automation.', connected: true, featured: false },
]

export default function IntegrationCatalog() {
  const navigate = useNavigate()

  return (
    <div className="fade-in">
      <div className="flex items-center gap-3 mb-6">
        <Plug className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Integrations</h1>
          <p className="text-sm text-gray-500 mt-1">Connect ExceptionOS to your existing tools and workflows.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {integrations.map(intg => (
          <div key={intg.id} className={`bg-white rounded-xl border p-5 ${intg.featured ? 'border-primary/30 bg-primary/3' : 'border-gray-200'}`}>
            {intg.featured && <div className="text-xs text-primary font-semibold mb-2">Featured Integration</div>}
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-sm font-semibold text-gray-900">{intg.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">{intg.category}</div>
              </div>
              {intg.connected && (
                <div className="flex items-center gap-1 text-xs text-green-700 font-medium">
                  <CheckCircle className="w-3.5 h-3.5" /> Connected
                </div>
              )}
            </div>
            <p className="text-sm text-gray-500 mb-4">{intg.desc}</p>
            <button
              onClick={() => intg.id === 'openclaw' ? navigate('/app/integrations/openclaw') : undefined}
              className={`w-full py-2 rounded-lg text-xs font-medium transition-colors ${intg.connected ? 'bg-gray-50 hover:bg-gray-100 text-gray-600 border border-gray-200' : 'bg-primary/10 hover:bg-primary/20 text-primary'}`}
            >
              {intg.connected ? 'Manage' : 'Connect'}
              {intg.id === 'openclaw' && <ExternalLink className="w-3 h-3 inline ml-1" />}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
