import { realApi } from './api'
import { demoApi } from './demo-api'
import { isDemo } from './demo'

export function useApi() {
  return isDemo() ? demoApi : realApi
}
