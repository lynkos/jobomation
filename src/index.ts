#!/usr/bin/env node
/**
 * jobomation  —  MCP Server
 *
 * This is the entry point. It creates an MCP server over stdio (the transport
 * OpenCode uses to communicate with plugins), registers all tools, and
 * dispatches incoming tool calls to the appropriate handler.
 *
 * To use this plugin with OpenCode, add to your ~/.opencode/config.json:
 *
 *   {
 *     "mcp": {
 *       "servers": {
 *         "jobomation": {
 *           "command": "node",
 *           "args": ["/path/to/jobomation/dist/index.js"]
 *         }
 *       }
 *     }
 *   }
 *
 * Then restart OpenCode and you'll have access to all tools listed below.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { SearchJobsInput, searchJobsHandler } from "./tools/search-jobs.js";
import { AnalyzeJobInput, analyzeJobHandler } from "./tools/analyze-job.js";
import { ApplyToJobInput, applyToJobHandler } from "./tools/apply-to-job.js";
import { ListApplicationsInput, listApplicationsHandler } from "./tools/list-applications.js";

// ─────────────────────────────────────────────
// Server initialization
// ─────────────────────────────────────────────

const server = new McpServer({
  name: "jobomation",
  version: "1.0.0",
});

// ─────────────────────────────────────────────
// Tool: search_jobs
// ─────────────────────────────────────────────

server.tool(
  "search_jobs",
  "Search LinkedIn, Indeed, and Greenhouse for job listings matching your query. " +
    "Results are saved to a local database. " +
    "Use analyze_job next to score a job against your resume, " +
    "or apply_to_job to immediately write a cover letter and submit.",
  SearchJobsInput.shape,
  async (args) => {
    const input = SearchJobsInput.parse(args);
    const text = await searchJobsHandler(input);
    return { content: [{ type: "text", text }] };
  }
);

// ─────────────────────────────────────────────
// Tool: analyze_job
// ─────────────────────────────────────────────

server.tool(
  "analyze_job",
  "Fetch the full description for a saved job and use Claude to score how well your " +
    "resume matches it. Returns a fit score (0–100), strengths, gaps, and a recommendation. " +
    "Requires the job to already be in the local database (run search_jobs first).",
  AnalyzeJobInput.shape,
  async (args) => {
    const input = AnalyzeJobInput.parse(args);
    const text = await analyzeJobHandler(input);
    return { content: [{ type: "text", text }] };
  }
);

// ─────────────────────────────────────────────
// Tool: apply_to_job
// ─────────────────────────────────────────────

server.tool(
  "apply_to_job",
  "Generate a tailored cover letter for a saved job using Claude, then automatically " +
    "submit the application via a headless browser. Supports LinkedIn Easy Apply and " +
    "Greenhouse ATS natively. Set dry_run=true to preview the cover letter without submitting. " +
    "Set headless=false to watch the browser in real time.",
  ApplyToJobInput.shape,
  async (args) => {
    const input = ApplyToJobInput.parse(args);
    const text = await applyToJobHandler(input);
    return { content: [{ type: "text", text }] };
  }
);

// ─────────────────────────────────────────────
// Tool: list_applications
// ─────────────────────────────────────────────

server.tool(
  "list_applications",
  "Display your job application tracker — a summary of all jobs in the local database " +
    "with their status, fit score, and application date. Filter by status or minimum score.",
  ListApplicationsInput.shape,
  async (args) => {
    const input = ListApplicationsInput.parse(args);
    const text = await listApplicationsHandler(input);
    return { content: [{ type: "text", text }] };
  }
);

// ─────────────────────────────────────────────
// Start server over stdio (OpenCode's transport)
// ─────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);

// Log to stderr (not stdout, which is reserved for MCP protocol messages)
console.error("[jobomation] MCP server running. Waiting for OpenCode...");
