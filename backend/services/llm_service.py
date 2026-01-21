import os
import json
import asyncio
from services.memory_service import MemoryService
from services.google_docs_service import GoogleDocsService
from services.google_sheets_service import GoogleSheetsService
from services.web_scraper_service import WebScraperService
from services.project_service import ProjectService
from services.gmail_service import GmailService
from services.contact_service import ContactService
from services.google_analytics_service import GoogleAnalyticsService

class LLMService:
    def __init__(self):
        # Get API key
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.model = "gemini-2.5-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        
        # Initialize memory service
        self.memory = MemoryService()
        
        # Initialize Google Docs service
        try:
            self.google_docs = GoogleDocsService()
        except Exception as e:
            print(f"Warning: Google Docs service not available: {e}")
            self.google_docs = None
        
        # Initialize Google Sheets service
        try:
            self.google_sheets = GoogleSheetsService()
        except Exception as e:
            print(f"Warning: Google Sheets service not available: {e}")
            self.google_sheets = None
        
        # Initialize Web Scraper service
        try:
            self.web_scraper = WebScraperService()
        except Exception as e:
            print(f"Warning: Web Scraper service not available: {e}")
            self.web_scraper = None
        
        # Initialize Project service
        try:
            self.projects = ProjectService()
        except Exception as e:
            print(f"Warning: Project service not available: {e}")
            self.projects = None
        
        # Initialize Gmail service
        try:
            self.gmail = GmailService()
            print(f"Gmail service initialized for: {self.gmail.get_user_email()}")
        except Exception as e:
            print(f"Warning: Gmail service not available: {e}")
            self.gmail = None
        
        # Initialize Contact service
        try:
            self.contacts = ContactService()
            print("Contact service initialized")
        except Exception as e:
            print(f"Warning: Contact service not available: {e}")
            self.contacts = None
        
        # Initialize Google Analytics service
        try:
            self.analytics = GoogleAnalyticsService()
            print("Google Analytics service initialized")
        except Exception as e:
            print(f"Warning: Google Analytics service not available: {e}")
            self.analytics = None
        
        self.system_prompt = """You are NAT (Not A Terminator), an elite SEO, AEO, and Search Intelligence AI designed to operate as a professional-grade SEO strategist, analyst, and execution engine.

🎯 YOUR CORE IDENTITY:
You are Bull's senior SEO consultant and strategic partner. You don't just answer questions - you analyze, decide, and execute.

🧠 HOW YOU THINK:
You think in terms of:
- User intent (informational, navigational, transactional, commercial)
- Entities and relationships (not keywords)
- SERP structure and competition
- Search engine behavior patterns
- Topical authority and content clusters
- Conversion impact and business value

🔍 YOUR CAPABILITIES:
You have access to these tools:
- Web scraping (browse_url, analyze_seo) - for competitor analysis and content research
- Google Docs/Sheets - for creating SEO briefs, content plans, and reports
- Gmail - send emails, create drafts, check inbox, search emails
- Contact management - Google Sheets contact list for email lookup by name
- Google Analytics - traffic data, top pages, traffic sources, realtime users
- Project management - for tracking SEO campaigns and optimization tasks
- Persistent memory - you remember past conversations and learn from Bull's business

🚨 CRITICAL RULES:

1. NEVER HALLUCINATE DATA
   - Don't invent search volumes, rankings, or traffic numbers
   - Use web scraping for real competitor data
   - Label assumptions clearly when live data unavailable
   - Say "I need to browse [URL] to get accurate data" when needed

2. MAKE DECISIONS, DON'T LIST OPTIONS
   - Analyze the situation
   - Choose the BEST option
   - Explain WHY it's the best choice
   - Provide clear next actions
   - No wishy-washy "here are some options" responses

3. THINK IN ENTITIES, NOT KEYWORDS
   - Google ranks entities, not keywords
   - Identify core entities (main topic)
   - Identify supporting entities (related concepts)
   - Detect missing entity coverage
   - Build topical authority, not isolated pages

4. STRUCTURE YOUR RESPONSES:
   ✅ Direct answer/recommendation FIRST (1-2 sentences)
   📊 Supporting reasoning with SEO logic
   🎯 Data-backed insights (from web scraping if available)
   ⚡ Clear next actions (numbered steps)

5. USE PROFESSIONAL TONE:
   - Confident and strategic
   - Precise, no filler
   - Senior SEO consultant voice
   - Brief but complete

🛠️ TOOL USAGE RULES:

When analyzing competitors:
→ Use browse_url to get their content structure
→ Use analyze_seo to check their optimization
→ Extract entities and topics they cover
→ Identify content gaps and opportunities

When creating SEO deliverables:
→ Use create_google_doc for content briefs
→ Use create_google_sheet for keyword research
→ Use create_project to track SEO campaigns

When sending emails:
→ If Bull provides a name instead of email, ALWAYS search contacts first
→ Use search_contact to find email addresses
→ Add new contacts when Bull provides contact info

When managing contacts:
→ ALWAYS ask "Are you sure you want to [add/update/delete] this contact?" before making changes
→ Wait for Bull's confirmation ("yes", "confirm", "do it", etc.) before proceeding
→ If Bull says "no" or "cancel", don't make the change

When Bull mentions a new project/client:
→ IMMEDIATELY create a project (don't ask permission)
→ Store domain, industry, and key details
→ If Bull provides a strategic objective, capture it EXACTLY as stated
→ Track it for future reference

When working on a project WITH a primary objective:
→ EVERY recommendation must align with that objective
→ Reference the objective when explaining your reasoning
→ Prioritize actions that directly advance the objective
→ Flag anything that conflicts with the objective

📋 OUTPUT STANDARDS:

For SEO analysis:
- Lead with the highest-impact finding
- Use tables for data comparison
- Provide specific, actionable recommendations
- Cite sources (URLs you browsed)

For content briefs:
- Target intent and entities first
- Outline structure for skimmability
- Include FAQ/schema opportunities
- Specify word count and format

For strategy:
- Prioritize by impact vs effort
- Explain the SEO logic
- Provide timeline estimates
- Flag dependencies or blockers

🎭 PERSONALITY:
You are Bull's trusted SEO expert. You:
- Speak directly and confidently
- Make strategic recommendations
- Focus on business impact
- Don't waste time with fluff
- Challenge assumptions when needed
- Celebrate wins and learn from data

IMPORTANT MEMORY CAPABILITIES:IMPORTANT MEMORY CAPABILITIES:
- You remember previous conversations across sessions
- You learn and store context about Bull's business over time
- You can recall past discussions, decisions, and preferences
- You grow smarter with each interaction

IMPORTANT: Default to brevity. Bull will ask follow-up questions if he wants more detail."""

    async def get_response(self, message: str, user_id: str = "bull", history: list = []):
        full_response = ""
        async for chunk in self.get_response_stream(message, user_id, history):
            full_response += chunk
        
        # Store the conversation in memory
        self.memory.add_conversation(user_id, message, full_response)
        self.memory.extract_and_store_context(user_id, message, full_response)
        
        return full_response

    async def get_response_stream(self, message: str, user_id: str = "bull", history: list = []):
        # Get user profile and conversation context
        user_profile = self.memory.get_user_profile(user_id)
        conversation_context = self.memory.get_conversation_context(user_id, limit=3)
        
        # Build context-aware prompt
        context = ""
        if conversation_context:
            context += conversation_context
        
        if user_profile.get("business_context"):
            context += "\n\nWhat I know about Bull's business:\n"
            for category, items in user_profile["business_context"].items():
                if items:
                    context += f"- {category.title()}: {', '.join(items[:3])}\n"
        
        # Add project context
        if self.projects:
            project_context = self.projects.get_project_context()
            if project_context:
                context += project_context
        
        # Add current conversation history to context (limit to last 10 messages)
        if history:
            context += "\n\nCurrent conversation:\n"
            # Take only the last 10 messages to keep context manageable
            recent_history = history[-10:] if len(history) > 10 else history
            for msg in recent_history:
                role = "Bull" if msg.get("role") == "user" else "NAT"
                msg_content = msg.get("content", "")
                # Truncate very long messages to avoid context overflow
                if len(msg_content) > 500:
                    msg_content = msg_content[:500] + "..."
                context += f"{role}: {msg_content}\n"
        
        # Build the final prompt with clear structure
        full_prompt = f"""{self.system_prompt}

{context}

===== IMPORTANT: READ THE CONVERSATION ABOVE CAREFULLY =====
Bull just said: {message}

Based on the conversation history above, respond as NAT:
"""
        
        # Debug: Print prompt info
        print(f"[DEBUG] Prompt length: {len(full_prompt)} characters")
        print(f"[DEBUG] History messages: {len(history) if history else 0}")
        
        # Define available tools for function calling
        tools = []
        if self.google_docs:
            tools.append({
                "function_declarations": [{
                    "name": "create_google_doc",
                    "description": "Create a new Google Doc with the specified title and content. Use this when Bull asks you to create a document, take notes, or document something.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the Google Doc to create"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to put in the Google Doc"
                            }
                        },
                        "required": ["title", "content"]
                    }
                }]
            })
        
        if self.google_sheets:
            tools.append({
                "function_declarations": [{
                    "name": "create_google_sheet",
                    "description": "Create a new Google Spreadsheet with the specified title and optional data. Use this when Bull asks you to create a spreadsheet, table, or organize data in a sheet.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the Google Sheet to create"
                            },
                            "data": {
                                "type": "array",
                                "description": "Optional 2D array of data to populate the sheet. Example: [['Name', 'Email'], ['John', 'john@example.com']]",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "required": ["title"]
                    }
                }]
            })
        
        # Add web browsing tools
        if self.web_scraper:
            tools.append({
                "function_declarations": [{
                    "name": "browse_url",
                    "description": "Fetch and analyze content from a website URL. Use this when Bull asks you to check a website, read web content, or analyze a page.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch and analyze"
                            }
                        },
                        "required": ["url"]
                    }
                }, {
                    "name": "analyze_seo",
                    "description": "Analyze SEO elements of a webpage including title tags, meta descriptions, headings, and images. Use when Bull asks about SEO analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to analyze for SEO"
                            }
                        },
                        "required": ["url"]
                    }
                }]
            })
        
        # Add project management tools
        if self.projects:
            tools.append({
                "function_declarations": [{
                    "name": "create_project",
                    "description": "Create a new project to track client/campaign information. Use when Bull mentions a new project, client, or campaign.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Project name"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Primary website domain"
                            },
                            "description": {
                                "type": "string",
                                "description": "Project description"
                            },
                            "industry": {
                                "type": "string",
                                "description": "Industry or sector"
                            },
                            "primary_objective": {
                                "type": "string",
                                "description": "Primary goal or objective for this project (e.g., 'Rank #1 for luxury Nashville real estate', 'Increase organic traffic by 50%')"
                            }
                        },
                        "required": ["name"]
                    }
                }, {
                    "name": "list_projects",
                    "description": "List all projects. Use when Bull asks about projects or wants to see what projects exist.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }, {
                    "name": "update_project",
                    "description": "Update an existing project's information. Use when Bull wants to modify project details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Project name to update"
                            },
                            "domain": {
                                "type": "string",
                                "description": "New domain (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description (optional)"
                            },
                            "industry": {
                                "type": "string",
                                "description": "New industry (optional)"
                            }
                        },
                        "required": ["name"]
                    }
                }, {
                    "name": "delete_project",
                    "description": "Delete a project. Use when Bull asks to remove or delete a project.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Project name to delete"
                            }
                        },
                        "required": ["name"]
                    }
                }]
            })
        
        # Add Gmail tools
        if self.gmail:
            tools.append({
                "function_declarations": [{
                    "name": "send_email",
                    "description": "Send an email via Gmail. Use when Bull asks to send an email or contact someone.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content (can include HTML)"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                }, {
                    "name": "draft_email",
                    "description": "Create a draft email for Bull to review before sending. Use when email needs review or approval.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                }, {
                    "name": "get_unread_emails",
                    "description": "Check inbox for unread emails. Use when Bull asks to check inbox or see new emails.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of emails to return (default 10)"
                            }
                        }
                    }
                }, {
                    "name": "search_emails",
                    "description": "Search emails by query. Use when Bull asks to find specific emails.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Gmail search query (e.g., 'from:example@email.com', 'subject:meeting')"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results (default 10)"
                            }
                        },
                        "required": ["query"]
                    }
                }, {
                    "name": "search_contact",
                    "description": "Look up a contact by name to get their email address. ALWAYS use this before sending emails if Bull provides a name instead of email.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Contact name to search for"
                            }
                        },
                        "required": ["name"]
                    }
                }, {
                    "name": "add_contact",
                    "description": "Add a new contact to the contact list. ALWAYS ask Bull for confirmation before adding.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Contact name"},
                            "email": {"type": "string", "description": "Email address"},
                            "phone": {"type": "string", "description": "Cell phone number"},
                            "description": {"type": "string", "description": "Contact description"}
                        },
                        "required": ["name", "email"]
                    }
                }, {
                    "name": "list_contacts",
                    "description": "List all contacts in the contact list",
                    "parameters": {"type": "object", "properties": {}}
                }, {
                    "name": "update_contact",
                    "description": "Update an existing contact. ALWAYS ask Bull for confirmation before updating.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Contact name to update"},
                            "email": {"type": "string", "description": "New email address"},
                            "phone": {"type": "string", "description": "New cell phone"},
                            "description": {"type": "string", "description": "New description"}
                        },
                        "required": ["name"]
                    }
                }, {
                    "name": "delete_contact",
                    "description": "Delete a contact. ALWAYS ask Bull for confirmation before deleting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Contact name to delete"}
                        },
                        "required": ["name"]
                    }
                }]
            })
        
        # Add Google Analytics tools
        if self.analytics:
            tools.append({
                "function_declarations": [{
                    "name": "get_analytics_overview",
                    "description": "Get Google Analytics traffic overview with sessions, users, pageviews, bounce rate, and avg session duration",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date (e.g., '30daysAgo', '2024-01-01')"},
                            "end_date": {"type": "string", "description": "End date (e.g., 'today', '2024-01-31')"}
                        }
                    }
                }, {
                    "name": "get_top_pages",
                    "description": "Get top performing pages with pageviews, avg time, and bounce rate",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date"},
                            "end_date": {"type": "string", "description": "End date"},
                            "limit": {"type": "number", "description": "Number of pages to return (default 10)"}
                        }
                    }
                }, {
                    "name": "get_traffic_sources",
                    "description": "Get traffic sources breakdown (organic, direct, referral, social, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date"},
                            "end_date": {"type": "string", "description": "End date"}
                        }
                    }
                }, {
                    "name": "get_realtime_users",
                    "description": "Get number of users currently active on the website",
                    "parameters": {"type": "object", "properties": {}}
                }]
            })
        
        # Add update functions
        if self.google_docs:
            tools[0]["function_declarations"].append({
                "name": "update_google_doc",
                "description": "Update an existing Google Doc by replacing its content. Use this when Bull asks you to edit, update, or modify an existing document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the Google Doc to update (from the URL)"
                        },
                        "content": {
                            "type": "string",
                            "description": "The new content to replace the document with"
                        }
                    },
                    "required": ["document_id", "content"]
                }
            })
        
        if self.google_sheets:
            # Find the sheets tool index
            for i, tool in enumerate(tools):
                if any(fd.get("name") == "create_google_sheet" for fd in tool.get("function_declarations", [])):
                    tools[i]["function_declarations"].append({
                        "name": "update_google_sheet",
                        "description": "Update an existing Google Sheet by adding or replacing data. Use this when Bull asks you to edit, update, or modify an existing spreadsheet.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "spreadsheet_id": {
                                    "type": "string",
                                    "description": "The ID of the Google Sheet to update (from the URL)"
                                },
                                "data": {
                                    "type": "array",
                                    "description": "2D array of data to add/update. Example: [['Name', 'Email'], ['John', 'john@example.com']]",
                                    "items": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "range_name": {
                                    "type": "string",
                                    "description": "Optional range in A1 notation (default: 'Sheet1')"
                                }
                            },
                            "required": ["spreadsheet_id", "data"]
                        }
                    })
                    break
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 8192,
            }
        }
        
        # Add tools if available
        if tools:
            payload["tools"] = tools
        
        url = f"{self.base_url}?key={self.api_key}"
        
        # Use aiohttp to get the full response
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                data = await response.json()
                
                # Check for function calls
                if 'candidates' in data:
                    for candidate in data['candidates']:
                        if 'content' in candidate:
                            for part in candidate['content'].get('parts', []):
                                # Handle function calls
                                if 'functionCall' in part:
                                    func_call = part['functionCall']
                                    if func_call['name'] == 'create_google_doc':
                                        args = func_call.get('args', {})
                                        result = await self.create_google_doc(
                                            args.get('title', 'Untitled Document'),
                                            args.get('content', '')
                                        )
                                        if result.get('success'):
                                            yield f"✅ Created Google Doc: [{result['title']}]({result['url']})"
                                        else:
                                            yield f"❌ Failed to create doc: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'create_google_sheet':
                                        args = func_call.get('args', {})
                                        result = await self.create_google_sheet(
                                            args.get('title', 'Untitled Spreadsheet'),
                                            args.get('data')
                                        )
                                        if result.get('success'):
                                            yield f"✅ Created Google Sheet: [{result['title']}]({result['url']})"
                                        else:
                                            yield f"❌ Failed to create sheet: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'update_google_doc':
                                        args = func_call.get('args', {})
                                        result = await self.update_google_doc(
                                            args.get('document_id'),
                                            args.get('content', '')
                                        )
                                        if result.get('success'):
                                            yield f"✅ Updated Google Doc: [{result['title']}]({result['url']})"
                                        else:
                                            yield f"❌ Failed to update doc: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'update_google_sheet':
                                        args = func_call.get('args', {})
                                        result = await self.update_google_sheet(
                                            args.get('spreadsheet_id'),
                                            args.get('data'),
                                            args.get('range_name', 'Sheet1')
                                        )
                                        if result.get('success'):
                                            yield f"✅ Updated Google Sheet: [{result['title']}]({result['url']})"
                                        else:
                                            yield f"❌ Failed to update sheet: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'browse_url':
                                        args = func_call.get('args', {})
                                        result = await self.browse_url(args.get('url'))
                                        if result.get('success'):
                                            summary = f"Title: {result['title']}\n\nContent preview: {result['content'][:500]}..."
                                            yield f"✅ Fetched {result['url']}\n\n{summary}"
                                        else:
                                            yield f"❌ Failed to browse URL: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'analyze_seo':
                                        args = func_call.get('args', {})
                                        result = await self.analyze_seo(args.get('url'))
                                        if result.get('success'):
                                            seo = result['seo_elements']
                                            summary = f"SEO Analysis for {result['url']}:\n"
                                            summary += f"- Title: {seo['title']['content']} ({seo['title']['length']} chars)\n"
                                            summary += f"- Meta Desc: {seo['meta_description']['length']} chars\n"
                                            summary += f"- H1 Tags: {seo['h1_tags']['count']}\n"
                                            summary += f"- Images: {seo['images']['total']} ({seo['images']['alt_text_coverage']} with alt text)"
                                            yield f"✅ {summary}"
                                        else:
                                            yield f"❌ Failed to analyze SEO: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'create_project':
                                        args = func_call.get('args', {})
                                        result = await self.create_project(
                                            args.get('name'),
                                            args.get('domain', ''),
                                            args.get('description', ''),
                                            args.get('industry', '')
                                        )
                                        if result.get('success'):
                                            proj = result['project']
                                            yield f"✅ Created project: {proj['name']}"
                                        else:
                                            yield f"❌ Failed to create project: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'list_projects':
                                        result = await self.list_projects()
                                        if result.get('success'):
                                            projects = result['projects']
                                            if projects:
                                                summary = f"Found {result['count']} projects:\n"
                                                for p in projects:
                                                    summary += f"- {p['name']}"
                                                    if p.get('domain'):
                                                        summary += f" ({p['domain']})"
                                                    summary += "\n"
                                                yield summary
                                            else:
                                                yield "No projects found."
                                        else:
                                            yield f"❌ Failed to list projects: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'update_project':
                                        args = func_call.get('args', {})
                                        updates = {}
                                        if args.get('domain'):
                                            updates['domain'] = args['domain']
                                        if args.get('description'):
                                            updates['description'] = args['description']
                                        if args.get('industry'):
                                            updates['industry'] = args['industry']
                                        result = await self.update_project(args.get('name'), **updates)
                                        if result.get('success'):
                                            yield f"✅ Updated project: {result['project']['name']}"
                                        else:
                                            yield f"❌ {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'delete_project':
                                        args = func_call.get('args', {})
                                        result = await self.delete_project(args.get('name'))
                                        if result.get('success'):
                                            yield f"✅ {result['message']}"
                                        else:
                                            yield f"❌ {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'send_email':
                                        args = func_call.get('args', {})
                                        result = await self.send_email(
                                            args.get('to'),
                                            args.get('subject'),
                                            args.get('body')
                                        )
                                        if result.get('success'):
                                            yield f"✅ Email sent to {args.get('to')}"
                                        else:
                                            yield f"❌ Failed to send email: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'draft_email':
                                        args = func_call.get('args', {})
                                        result = await self.draft_email(
                                            args.get('to'),
                                            args.get('subject'),
                                            args.get('body')
                                        )
                                        if result.get('success'):
                                            yield f"✅ Draft created for {args.get('to')} - review in Gmail"
                                        else:
                                            yield f"❌ Failed to create draft: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'get_unread_emails':
                                        args = func_call.get('args', {})
                                        result = await self.get_unread_emails(args.get('max_results', 10))
                                        if result.get('success'):
                                            if result['count'] == 0:
                                                yield "📭 No unread emails"
                                            else:
                                                summary = f"📬 {result['count']} unread email(s):\n\n"
                                                for email in result['emails']:
                                                    summary += f"From: {email['from']}\n"
                                                    summary += f"Subject: {email['subject']}\n"
                                                    summary += f"Preview: {email['snippet'][:100]}...\n\n"
                                                yield summary
                                        else:
                                            yield f"❌ Failed to get emails: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'search_emails':
                                        args = func_call.get('args', {})
                                        result = await self.search_emails(args.get('query'), args.get('max_results', 10))
                                        if result.get('success'):
                                            if result['count'] == 0:
                                                yield f"🔍 No emails found for query: {result.get('query')}"
                                            else:
                                                summary = f"🔍 Found {result['count']} email(s) for '{result.get('query')}':\n\n"
                                                for email in result['emails']:
                                                    summary += f"From: {email['from']}\n"
                                                    summary += f"Subject: {email['subject']}\n"
                                                    summary += f"Date: {email['date']}\n\n"
                                                yield summary
                                        else:
                                            yield f"❌ Failed to search emails: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'search_contact':
                                        args = func_call.get('args', {})
                                        result = await self.search_contact(args.get('name'))
                                        if result.get('success'):
                                            contact = result['contact']
                                            yield f"📇 Found: {contact['name']} - {contact['email']}"
                                            if contact.get('company'):
                                                yield f" ({contact['company']})"
                                        else:
                                            yield f"❌ {result.get('error', 'Contact not found')}"
                                    elif func_call['name'] == 'add_contact':
                                        args = func_call.get('args', {})
                                        result = await self.add_contact(
                                            args.get('name'),
                                            args.get('email'),
                                            args.get('phone', ''),
                                            args.get('description', '')
                                        )
                                        if result.get('success'):
                                            yield f"✅ {result['message']}"
                                        else:
                                            yield f"❌ Failed to add contact: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'list_contacts':
                                        result = await self.list_contacts()
                                        if result.get('success'):
                                            if result['count'] == 0:
                                                yield "📇 No contacts found"
                                            else:
                                                summary = f"📇 {result['count']} contact(s):\n\n"
                                                for contact in result['contacts']:
                                                    summary += f"**{contact['name']}**\n"
                                                    summary += f"  Email: {contact['email']}\n"
                                                    if contact.get('phone'):
                                                        summary += f"  Phone: {contact['phone']}\n"
                                                    if contact.get('description'):
                                                        summary += f"  Description: {contact['description']}\n"
                                                    summary += "\n"
                                                yield summary
                                        else:
                                            yield f"❌ Failed to list contacts: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'update_contact':
                                        args = func_call.get('args', {})
                                        result = await self.update_contact(
                                            args.get('name'),
                                            args.get('email'),
                                            args.get('phone'),
                                            args.get('description')
                                        )
                                        if result.get('success'):
                                            yield f"✅ {result['message']}"
                                        else:
                                            yield f"❌ Failed to update contact: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'delete_contact':
                                        args = func_call.get('args', {})
                                        result = await self.delete_contact(args.get('name'))
                                        if result.get('success'):
                                            yield f"✅ {result['message']}"
                                        else:
                                            yield f"❌ Failed to delete contact: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'get_analytics_overview':
                                        args = func_call.get('args', {})
                                        result = await self.get_analytics_overview(
                                            start_date=args.get('start_date', '30daysAgo'),
                                            end_date=args.get('end_date', 'today')
                                        )
                                        if result.get('success'):
                                            data = result['data']
                                            summary = f"📊 **Analytics Overview** ({result['date_range']})\n\n"
                                            summary += f"**Sessions:** {data['sessions']:,}\n"
                                            summary += f"**Users:** {data['users']:,}\n"
                                            summary += f"**Pageviews:** {data['pageviews']:,}\n"
                                            summary += f"**Bounce Rate:** {data['bounce_rate']}\n"
                                            summary += f"**Avg Session Duration:** {data['avg_session_duration']}"
                                            yield summary
                                        else:
                                            yield f"❌ Failed to get analytics: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'get_top_pages':
                                        args = func_call.get('args', {})
                                        result = await self.get_top_pages(
                                            start_date=args.get('start_date', '30daysAgo'),
                                            end_date=args.get('end_date', 'today'),
                                            limit=args.get('limit', 10)
                                        )
                                        if result.get('success'):
                                            summary = f"📄 **Top {result['count']} Pages** ({result['date_range']})\n\n"
                                            for i, page in enumerate(result['pages'], 1):
                                                summary += f"{i}. **{page['title']}**\n"
                                                summary += f"   Path: {page['path']}\n"
                                                summary += f"   Pageviews: {page['pageviews']:,} | Avg Time: {page['avg_time']} | Bounce: {page['bounce_rate']}\n\n"
                                            yield summary
                                        else:
                                            yield f"❌ Failed to get top pages: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'get_traffic_sources':
                                        args = func_call.get('args', {})
                                        result = await self.get_traffic_sources(
                                            start_date=args.get('start_date', '30daysAgo'),
                                            end_date=args.get('end_date', 'today')
                                        )
                                        if result.get('success'):
                                            summary = f"🌐 **Traffic Sources** ({result['date_range']})\n\n"
                                            for source in result['sources']:
                                                summary += f"**{source['source']}** / {source['medium']}\n"
                                                summary += f"   Sessions: {source['sessions']:,} | Users: {source['users']:,}\n\n"
                                            yield summary
                                        else:
                                            yield f"❌ Failed to get traffic sources: {result.get('error', 'Unknown error')}"
                                    elif func_call['name'] == 'get_realtime_users':
                                        result = await self.get_realtime_users()
                                        if result.get('success'):
                                            yield f"👥 **{result['active_users']} users** currently active on the site"
                                        else:
                                            yield f"❌ Failed to get realtime data: {result.get('error', 'Unknown error')}"
                                # Handle text responses
                                elif 'text' in part:
                                    # Stream word by word for better UX
                                    text = part['text']
                                    words = text.split(' ')
                                    for i, word in enumerate(words):
                                        if i < len(words) - 1:
                                            yield word + ' '
                                        else:
                                            yield word
                                        # Removed artificial delay for instant responses
    
    async def create_google_doc(self, title: str, content: str):
        """Create a Google Doc with the given title and content"""
        if not self.google_docs:
            return {"error": "Google Docs service not available"}
        
        try:
            result = self.google_docs.create_document(title, content)
            return {
                "success": True,
                "title": result["title"],
                "url": result["url"],
                "id": result["id"]
            }
        except Exception as e:
            return {"error": str(e)}

    async def create_google_sheet(self, title: str, data=None):
        """Create a Google Sheet with the given title and optional data"""
        if not self.google_sheets:
            return {"error": "Google Sheets service not available"}
        
        try:
            result = self.google_sheets.create_spreadsheet(title, data)
            return {
                "success": True,
                "title": result["title"],
                "url": result["url"],
                "id": result["id"]
            }
        except Exception as e:
            return {"error": str(e)}

    async def update_google_doc(self, document_id: str, content: str):
        """Update an existing Google Doc with new content"""
        if not self.google_docs:
            return {"error": "Google Docs service not available"}
        
        try:
            self.google_docs.update_document(document_id, content)
            # Get document info
            file = self.google_docs.drive_service.files().get(
                fileId=document_id,
                fields='name,webViewLink'
            ).execute()
            
            return {
                "success": True,
                "title": file.get('name'),
                "url": file.get('webViewLink'),
                "id": document_id
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def update_google_sheet(self, spreadsheet_id: str, data, range_name='Sheet1'):
        """Update an existing Google Sheet with new data"""
        if not self.google_sheets:
            return {"error": "Google Sheets service not available"}
        
        try:
            self.google_sheets.add_data(spreadsheet_id, data, range_name)
            # Get spreadsheet info
            spreadsheet = self.google_sheets.get_spreadsheet(spreadsheet_id)
            
            return {
                "success": True,
                "title": spreadsheet['properties']['title'],
                "url": spreadsheet.get('spreadsheetUrl'),
                "id": spreadsheet_id
            }
        except Exception as e:
            return {"error": str(e)}

    async def browse_url(self, url: str):
        """Fetch and analyze content from a URL"""
        if not self.web_scraper:
            return {"error": "Web scraper service not available"}
        
        try:
            result = self.web_scraper.fetch_url(url)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_seo(self, url: str):
        """Analyze SEO elements of a webpage"""
        if not self.web_scraper:
            return {"error": "Web scraper service not available"}
        
        try:
            result = self.web_scraper.analyze_seo(url)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def create_project(self, name: str, domain: str = "", description: str = "", industry: str = "", primary_objective: str = ""):
        """Create a new project"""
        if not self.projects:
            return {"error": "Project service not available"}
        
        try:
            project = self.projects.create_project(name, domain, description, industry, primary_objective)
            return {
                "success": True,
                "project": project
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_project(self, name: str):
        """Get a project by name"""
        if not self.projects:
            return {"error": "Project service not available"}
        
        try:
            project = self.projects.get_project(name=name)
            if project:
                return {
                    "success": True,
                    "project": project
                }
            else:
                return {"error": f"Project '{name}' not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def list_projects(self):
        """List all projects"""
        if not self.projects:
            return {"error": "Project service not available"}
        
        try:
            projects = self.projects.list_projects()
            return {
                "success": True,
                "projects": projects,
                "count": len(projects)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def update_project(self, name: str, **updates):
        """Update a project"""
        if not self.projects:
            return {"error": "Project service not available"}
        
        try:
            # Find project by name
            project = self.projects.get_project(name=name)
            if not project:
                return {"error": f"Project '{name}' not found"}
            
            # Update it
            updated = self.projects.update_project(project['id'], **updates)
            if updated:
                return {
                    "success": True,
                    "project": updated
                }
            else:
                return {"error": "Failed to update project"}
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_project(self, name: str):
        """Delete a project"""
        if not self.projects:
            return {"error": "Project service not available"}
        
        try:
            # Find project by name
            project = self.projects.get_project(name=name)
            if not project:
                return {"error": f"Project '{name}' not found"}
            
            # Delete it
            deleted = self.projects.delete_project(project['id'])
            if deleted:
                return {
                    "success": True,
                    "message": f"Deleted project '{name}'"
                }
            else:
                return {"error": "Failed to delete project"}
        except Exception as e:
            return {"error": str(e)}

    async def send_email(self, to: str, subject: str, body: str):
        """Send an email via Gmail"""
        if not self.gmail:
            return {"error": "Gmail service not available"}
        
        try:
            result = self.gmail.send_email(to, subject, body)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def draft_email(self, to: str, subject: str, body: str):
        """Create a draft email for review"""
        if not self.gmail:
            return {"error": "Gmail service not available"}
        
        try:
            result = self.gmail.draft_email(to, subject, body)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def get_unread_emails(self, max_results: int = 10):
        """Get unread emails from inbox"""
        if not self.gmail:
            return {"error": "Gmail service not available"}
        
        try:
            result = self.gmail.get_unread_emails(max_results)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def search_emails(self, query: str, max_results: int = 10):
        """Search emails by query"""
        if not self.gmail:
            return {"error": "Gmail service not available"}
        
        try:
            result = self.gmail.search_emails(query, max_results)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def search_contact(self, name: str):
        """Search for a contact by name"""
        if not self.contacts:
            return {"error": "Contact service not available"}
        
        try:
            result = self.contacts.search_contact(name)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def add_contact(self, name: str, email: str, phone: str = "", description: str = ""):
        """Add a new contact"""
        if not self.contacts:
            return {"error": "Contact service not available"}
        
        try:
            result = self.contacts.add_contact(name, email, phone, description)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def list_contacts(self):
        """List all contacts"""
        if not self.contacts:
            return {"error": "Contact service not available"}
        
        try:
            result = self.contacts.list_all_contacts()
            return result
        except Exception as e:
            return {"error": str(e)}

    async def update_contact(self, name: str, email: str = None, phone: str = None, description: str = None):
        """Update an existing contact"""
        if not self.contacts:
            return {"error": "Contact service not available"}
        
        try:
            result = self.contacts.update_contact(name, email, phone, description)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_contact(self, name: str):
        """Delete a contact"""
        if not self.contacts:
            return {"error": "Contact service not available"}
        
        try:
            result = self.contacts.delete_contact(name)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def get_analytics_overview(self, property_id: str = None, start_date: str = "30daysAgo", end_date: str = "today"):
        """Get Google Analytics overview"""
        if not self.analytics:
            return {"error": "Google Analytics service not available"}
        
        # Use default property ID if not provided
        if not property_id:
            property_id = os.getenv('GA4_PROPERTY_ID', '356759519')
        
        try:
            result = self.analytics.get_analytics_overview(property_id, start_date, end_date)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def get_top_pages(self, property_id: str = None, start_date: str = "30daysAgo", end_date: str = "today", limit: int = 10):
        """Get top performing pages"""
        if not self.analytics:
            return {"error": "Google Analytics service not available"}
        
        if not property_id:
            property_id = os.getenv('GA4_PROPERTY_ID', '356759519')
        
        try:
            result = self.analytics.get_top_pages(property_id, start_date, end_date, limit)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def get_traffic_sources(self, property_id: str = None, start_date: str = "30daysAgo", end_date: str = "today"):
        """Get traffic sources"""
        if not self.analytics:
            return {"error": "Google Analytics service not available"}
        
        if not property_id:
            property_id = os.getenv('GA4_PROPERTY_ID', '356759519')
        
        try:
            result = self.analytics.get_traffic_sources(property_id, start_date, end_date)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def get_realtime_users(self, property_id: str = None):
        """Get real-time active users"""
        if not self.analytics:
            return {"error": "Google Analytics service not available"}
        
        if not property_id:
            property_id = os.getenv('GA4_PROPERTY_ID', '356759519')
        
        try:
            result = self.analytics.get_realtime_data(property_id)
            return result
        except Exception as e:
            return {"error": str(e)}
