import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export default function proxy(request: NextRequest) {
  const refreshToken = request.cookies.get('refresh_token');
  const { pathname } = request.nextUrl;

  // Protected routes
  const protectedRoutes = ['/dashboard', '/tasks'];
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

  // If protected route and no refresh token, redirect to login
  if (isProtectedRoute && !refreshToken) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If auth route and has refresh token, redirect to dashboard
  const authRoutes = ['/login', '/register'];
  const isAuthRoute = authRoutes.includes(pathname);
  if (isAuthRoute && refreshToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
