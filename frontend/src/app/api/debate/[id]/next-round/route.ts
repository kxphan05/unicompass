const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;

  const upstream = await fetch(`${BACKEND}/api/debate/${id}/next-round`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  const data = await upstream.json();
  return Response.json(data, { status: upstream.status });
}
