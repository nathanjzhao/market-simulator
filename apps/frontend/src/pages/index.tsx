
import Link from 'next/link';

export default function Home() {

  return (
    <div>
      <h1>Welcome to the Home Page</h1>
      <Link id="register" href="/register">
        Go to Register
      </Link>
      <Link id="login" href="/login">
        Go to Login
      </Link>
    </div>
  );
}