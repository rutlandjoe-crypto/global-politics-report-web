import { NextResponse } from "next/server";
import report from "../../../public/latest_report.json";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  return NextResponse.json(report, {
    headers: {
      "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
      "X-GSR-Report-Source": "repository-publication",
    },
  });
}
