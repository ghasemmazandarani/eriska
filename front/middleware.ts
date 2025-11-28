import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
    // We can't access localStorage in middleware, so we rely on client-side checks 
    // or cookies if we implemented them. 
    // For this simple implementation, we'll skip strict middleware checks 
    // and rely on the API interceptors and client-side redirects for now,
    // as we are storing tokens in localStorage (not accessible here).

    // However, if we move to cookies later, this is where we'd check them.
    return NextResponse.next()
}

export const config = {
    matcher: '/dashboard/:path*',
}
