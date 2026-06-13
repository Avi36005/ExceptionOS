import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'

// Public pages
import LandingPage from './pages/public/LandingPage'
import LoginPage from './pages/public/LoginPage'
import SignupPage from './pages/public/SignupPage'
import ForgotPasswordPage from './pages/public/ForgotPasswordPage'
import ResetPasswordPage from './pages/public/ResetPasswordPage'
import AuthCallbackPage from './pages/public/AuthCallbackPage'
import AcceptInvitePage from './pages/public/AcceptInvitePage'
import UnauthorizedPage from './pages/public/UnauthorizedPage'

// Onboarding
import OnboardingLayout from './pages/onboarding/OnboardingLayout'
import CompanySetup from './pages/onboarding/CompanySetup'
import PoliciesSetup from './pages/onboarding/PoliciesSetup'
import TeamSetup from './pages/onboarding/TeamSetup'
import HindsightSetup from './pages/onboarding/HindsightSetup'
import SelectOrg from './pages/onboarding/SelectOrg'

// App shell
import AppShell from './components/layout/AppShell'

// App pages
import Dashboard from './pages/app/Dashboard'
import Inbox from './pages/app/Inbox'
import MyRequests from './pages/app/MyRequests'
import MyApprovals from './pages/app/MyApprovals'

// Exceptions
import NewException from './pages/app/exceptions/NewException'
import ExceptionDetail from './pages/app/exceptions/ExceptionDetail'
import ExceptionIntake from './pages/app/exceptions/ExceptionIntake'
import ExceptionEvidence from './pages/app/exceptions/ExceptionEvidence'
import ExceptionPolicy from './pages/app/exceptions/ExceptionPolicy'
import ExceptionPrecedents from './pages/app/exceptions/ExceptionPrecedents'
import ExceptionDebate from './pages/app/exceptions/ExceptionDebate'
import ExceptionRecommendation from './pages/app/exceptions/ExceptionRecommendation'
import ExceptionDecision from './pages/app/exceptions/ExceptionDecision'
import ExceptionOutcome from './pages/app/exceptions/ExceptionOutcome'
import ExceptionAudit from './pages/app/exceptions/ExceptionAudit'
import ExceptionMemory from './pages/app/exceptions/ExceptionMemory'

// Policies
import PolicyLibrary from './pages/app/policies/PolicyLibrary'
import NewPolicy from './pages/app/policies/NewPolicy'
import PolicyDetail from './pages/app/policies/PolicyDetail'
import PolicyEdit from './pages/app/policies/PolicyEdit'
import PolicyVersions from './pages/app/policies/PolicyVersions'
import PolicyDrift from './pages/app/policies/PolicyDrift'
import PolicySimulator from './pages/app/policies/PolicySimulator'

// Precedents
import PrecedentSearch from './pages/app/precedents/PrecedentSearch'
import PrecedentDetail from './pages/app/precedents/PrecedentDetail'
import PrecedentGraph from './pages/app/precedents/PrecedentGraph'
import PrecedentAsk from './pages/app/precedents/PrecedentAsk'

// Insights
import InsightsDashboard from './pages/app/insights/InsightsDashboard'
import PolicyDriftInsights from './pages/app/insights/PolicyDriftInsights'
import RepeatedExceptions from './pages/app/insights/RepeatedExceptions'
import MemoryHealth from './pages/app/insights/MemoryHealth'
import ProviderUsage from './pages/app/insights/ProviderUsage'

// Training
import TrainingLibrary from './pages/app/training/TrainingLibrary'
import TrainingScenario from './pages/app/training/TrainingScenario'

// Voice
import VoiceAssistant from './pages/app/voice/VoiceAssistant'

// Integrations
import IntegrationCatalog from './pages/app/integrations/IntegrationCatalog'
import OpenClawIntegration from './pages/app/integrations/OpenClawIntegration'

// Admin
import Organizations from './pages/app/admin/Organizations'
import Users from './pages/app/admin/Users'
import Roles from './pages/app/admin/Roles'
import Departments from './pages/app/admin/Departments'
import EscalationRules from './pages/app/admin/EscalationRules'
import SLAConfig from './pages/app/admin/SLAConfig'
import Budgets from './pages/app/admin/Budgets'
import Categories from './pages/app/admin/Categories'
import SystemHealth from './pages/app/admin/SystemHealth'

// Settings
import Profile from './pages/app/settings/Profile'
import OrgSettings from './pages/app/settings/OrgSettings'
import Notifications from './pages/app/settings/Notifications'
import Security from './pages/app/settings/Security'
import DemoMode from './pages/app/settings/DemoMode'

// Demo
import DemoLauncher from './pages/app/demo/DemoLauncher'
import DemoStory from './pages/app/demo/DemoStory'
import HindsightLive from './pages/app/demo/HindsightLive'
import BeforeAfter from './pages/app/demo/BeforeAfter'

import LoadingSpinner from './components/ui/LoadingSpinner'

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, initialized } = useAuthStore()
  if (!initialized) return <div className="min-h-screen flex items-center justify-center bg-dark"><LoadingSpinner size="lg" /></div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const { initialize } = useAuthStore()

  useEffect(() => {
    initialize()
  }, [initialize])

  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0C0F24',
            color: '#F4F5FA',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '10px',
          },
          success: { iconTheme: { primary: '#5B5BF0', secondary: '#fff' } },
        }}
      />
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/accept-invite" element={<AcceptInvitePage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />
        <Route path="/service-unavailable" element={<UnauthorizedPage />} />

        {/* Onboarding */}
        <Route path="/select-organization" element={<AuthGuard><SelectOrg /></AuthGuard>} />
        <Route path="/onboarding" element={<AuthGuard><OnboardingLayout /></AuthGuard>}>
          <Route path="company" element={<CompanySetup />} />
          <Route path="policies" element={<PoliciesSetup />} />
          <Route path="team" element={<TeamSetup />} />
          <Route path="hindsight" element={<HindsightSetup />} />
        </Route>

        {/* Demo */}
        <Route path="/demo" element={<DemoLauncher />} />
        <Route path="/demo/story" element={<DemoStory />} />
        <Route path="/demo/hindsight-live" element={<HindsightLive />} />
        <Route path="/demo/before-after" element={<BeforeAfter />} />

        {/* App */}
        <Route path="/app" element={<AuthGuard><AppShell /></AuthGuard>}>
          <Route index element={<Dashboard />} />
          <Route path="inbox" element={<Inbox />} />
          <Route path="my-requests" element={<MyRequests />} />
          <Route path="my-approvals" element={<MyApprovals />} />

          {/* Exceptions */}
          <Route path="exceptions/new" element={<NewException />} />
          <Route path="exceptions/:caseId" element={<ExceptionDetail />}>
            <Route path="intake" element={<ExceptionIntake />} />
            <Route path="evidence" element={<ExceptionEvidence />} />
            <Route path="policy" element={<ExceptionPolicy />} />
            <Route path="precedents" element={<ExceptionPrecedents />} />
            <Route path="debate" element={<ExceptionDebate />} />
            <Route path="recommendation" element={<ExceptionRecommendation />} />
            <Route path="decision" element={<ExceptionDecision />} />
            <Route path="outcome" element={<ExceptionOutcome />} />
            <Route path="replay" element={<ExceptionAudit />} />
            <Route path="audit" element={<ExceptionAudit />} />
            <Route path="what-changed" element={<ExceptionRecommendation />} />
            <Route path="memory" element={<ExceptionMemory />} />
          </Route>

          {/* Policies */}
          <Route path="policies" element={<PolicyLibrary />} />
          <Route path="policies/new" element={<NewPolicy />} />
          <Route path="policies/drift" element={<PolicyDrift />} />
          <Route path="policies/simulator" element={<PolicySimulator />} />
          <Route path="policies/autopilot" element={<PolicySimulator />} />
          <Route path="policies/:policyId" element={<PolicyDetail />} />
          <Route path="policies/:policyId/edit" element={<PolicyEdit />} />
          <Route path="policies/:policyId/versions" element={<PolicyVersions />} />
          <Route path="policies/:policyId/exceptions" element={<PolicyDetail />} />
          <Route path="policies/:policyId/drift" element={<PolicyDrift />} />

          {/* Precedents */}
          <Route path="precedents" element={<PrecedentSearch />} />
          <Route path="precedents/graph" element={<PrecedentGraph />} />
          <Route path="precedents/compare" element={<PrecedentSearch />} />
          <Route path="precedents/contradictions" element={<PrecedentSearch />} />
          <Route path="precedents/ask" element={<PrecedentAsk />} />
          <Route path="precedents/:precedentId" element={<PrecedentDetail />} />

          {/* Insights */}
          <Route path="insights" element={<InsightsDashboard />} />
          <Route path="insights/policy-drift" element={<PolicyDriftInsights />} />
          <Route path="insights/repeated" element={<RepeatedExceptions />} />
          <Route path="insights/repeated-exceptions" element={<RepeatedExceptions />} />
          <Route path="insights/root-causes" element={<InsightsDashboard />} />
          <Route path="insights/consistency" element={<InsightsDashboard />} />
          <Route path="insights/outcomes" element={<InsightsDashboard />} />
          <Route path="insights/success" element={<InsightsDashboard />} />
          <Route path="insights/budgets" element={<InsightsDashboard />} />
          <Route path="insights/benchmarks" element={<InsightsDashboard />} />
          <Route path="insights/memory-health" element={<MemoryHealth />} />
          <Route path="insights/providers" element={<ProviderUsage />} />
          <Route path="insights/provider-usage" element={<ProviderUsage />} />

          {/* Training */}
          <Route path="training" element={<TrainingLibrary />} />
          <Route path="training/history" element={<TrainingLibrary />} />
          <Route path="training/team" element={<TrainingLibrary />} />
          <Route path="training/scenarios/:scenarioId" element={<TrainingScenario />} />
          <Route path="training/:scenarioId" element={<TrainingScenario />} />

          {/* Voice */}
          <Route path="voice" element={<VoiceAssistant />} />
          <Route path="voice/history" element={<VoiceAssistant />} />
          <Route path="voice/:sessionId" element={<VoiceAssistant />} />

          {/* Integrations */}
          <Route path="integrations" element={<IntegrationCatalog />} />
          <Route path="integrations/openclaw" element={<OpenClawIntegration />} />
          <Route path="integrations/elevenlabs" element={<IntegrationCatalog />} />
          <Route path="integrations/hindsight" element={<IntegrationCatalog />} />

          {/* Admin */}
          <Route path="admin/organizations" element={<Organizations />} />
          <Route path="admin/users" element={<Users />} />
          <Route path="admin/roles" element={<Roles />} />
          <Route path="admin/departments" element={<Departments />} />
          <Route path="admin/escalation" element={<EscalationRules />} />
          <Route path="admin/sla" element={<SLAConfig />} />
          <Route path="admin/budgets" element={<Budgets />} />
          <Route path="admin/categories" element={<Categories />} />
          <Route path="admin/system" element={<SystemHealth />} />

          {/* Settings */}
          <Route path="settings/profile" element={<Profile />} />
          <Route path="settings/org" element={<OrgSettings />} />
          <Route path="settings/notifications" element={<Notifications />} />
          <Route path="settings/security" element={<Security />} />
          <Route path="settings/demo" element={<DemoMode />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
