import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="max-w-2xl text-center">
        <h1 className="text-5xl font-bold tracking-tight mb-4">
          Uni<span className="text-blue-600">Compass</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered university advisor for Singapore students. Watch NUS and NTU debate why
          you should pick them — based on your actual A-Level results.
        </p>
        <Link
          href="/profile"
          className="inline-block rounded-lg bg-blue-600 px-8 py-4 text-lg font-medium text-white hover:bg-blue-700 transition-colors"
        >
          Get Started
        </Link>
      </div>
    </main>
  );
}
