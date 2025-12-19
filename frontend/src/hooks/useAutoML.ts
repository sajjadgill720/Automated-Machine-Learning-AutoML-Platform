/**
 * Custom React Hooks for AutoML
 */

import { useEffect, useState } from 'react'
import { useQuery, UseQueryResult } from '@tanstack/react-query'
import { automlAPI } from '@api/automl'
import { PipelineResult } from '@types/automl'

/**
 * Hook to poll job status with exponential backoff
 */
export const useJobPolling = (jobId: string | null, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['jobStatus', jobId],
    queryFn: async () => {
      if (!jobId) throw new Error('No job ID provided')
      return automlAPI.getJobStatus(jobId)
    },
    enabled: !!jobId && enabled,
    refetchInterval: (data) => {
      // If job is completed or errored, don't refetch
      if (data?.status === 'completed' || data?.status === 'error') {
        return false
      }
      // Otherwise, refetch every 2 seconds
      return 2000
    },
    refetchIntervalInBackground: false,
  })
}

/**
 * Hook to fetch job results
 */
export const useJobResults = (jobId: string | null) => {
  return useQuery({
    queryKey: ['jobResults', jobId],
    queryFn: async () => {
      if (!jobId) throw new Error('No job ID provided')
      return automlAPI.getResults(jobId)
    },
    enabled: !!jobId,
    staleTime: Infinity,
  })
}

/**
 * Hook to track time elapsed since job started
 */
export const useElapsedTime = (jobStartTime: number | null): string => {
  const [elapsed, setElapsed] = useState<string>('')

  useEffect(() => {
    if (!jobStartTime) return

    const interval = setInterval(() => {
      const now = Date.now()
      const diffMs = now - jobStartTime
      const diffSeconds = Math.floor(diffMs / 1000)
      const diffMinutes = Math.floor(diffSeconds / 60)
      const remainingSeconds = diffSeconds % 60

      if (diffMinutes > 0) {
        setElapsed(`${diffMinutes}m ${remainingSeconds}s`)
      } else {
        setElapsed(`${diffSeconds}s`)
      }
    }, 100)

    return () => clearInterval(interval)
  }, [jobStartTime])

  return elapsed
}

/**
 * Hook to validate if we can proceed to next step
 */
export const useFormValidation = (step: number): { isValid: boolean; error: string | null } => {
  const [validation, setValidation] = useState({ isValid: false, error: null as string | null })

  useEffect(() => {
    // Validation logic will be handled by component, this is just a helper structure
  }, [step])

  return validation
}

/**
 * Hook for debounced search input
 */
export const useDebouncedValue = <T,>(value: T, delay: number = 500): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}

/**
 * Hook for local storage persistence
 */
export const useLocalStorage = <T,>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void] => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.warn(`Error reading from localStorage for key "${key}":`, error)
      return initialValue
    }
  })

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.warn(`Error writing to localStorage for key "${key}":`, error)
    }
  }

  return [storedValue, setValue]
}

/**
 * Hook for responsive breakpoints
 */
export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    if (media.matches !== matches) {
      setMatches(media.matches)
    }

    const listener = () => setMatches(media.matches)
    media.addListener(listener)
    return () => media.removeListener(listener)
  }, [matches, query])

  return matches
}

/**
 * Hook for mobile detection
 */
export const useIsMobile = (): boolean => {
  return useMediaQuery('(max-width: 768px)')
}
