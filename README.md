# CreativeIQ

Building an effective marketing campaign requires more than creating attractive visuals. Businesses need to understand their target audience, analyse competitors, establish a distinct brand identity, develop a relevant marketing strategy, and consistently produce engaging content. For startups, small businesses, and emerging brands, managing all these activities can be difficult due to limited budgets, resources, and access to professional marketing teams.

CREATIVEIQ acts as a virtual creative agency consisting of specialised agents that collaborate throughout the campaign development process. A user provides a basic description of their brand, product, target audience, and marketing objectives. The system processes this information through three primary stages:

Brand Intelligence: Understands the brand, researches competitors, identifies the target audience, and establishes the brand's identity.
Autonomous Creative Direction: Develops multiple campaign concepts, evaluates their suitability, selects a direction, and prepares a detailed creative brief.
Creative and Image Generation: Converts the approved creative brief into detailed visual prompts and generates marketing assets using an external image-generation service.

Complete Agent Workflow :-

                    USER
                      |
                      v
               BRAND BRIEF INPUT
                      |
                      v
              INPUT VALIDATION
                      |
                      v
             SHARED CAMPAIGN STATE
                      |
                      v
       +-----------------------------+
       |   AGENT 1: BRAND INTELLIGENCE|
       +-----------------------------+
                      |
             Brand DNA and Research
                      |
                      v
       +-----------------------------+
       |  AGENT 2: CREATIVE DIRECTOR |
       +-----------------------------+
                      |
          Campaign Concepts and Strategy
                      |
                      v
               USER APPROVAL
                      |
                      v
       +-----------------------------+
       | AGENT 3: CREATIVE GENERATOR  |
       +-----------------------------+
                      |
             Visual Prompt Creation
                      |
                      v
           IMAGE GENERATION API
                      |
                      v
              IMAGE VALIDATION
                      |
                      v
              CLOUDINARY STORAGE
                      |
                      v
              FINAL CAMPAIGN KIT
                      |
                      v
                   USER

Tech Stack :- 
Python, Groq API, Langraph, FastAPI, Pydantic, Tavily API, Gemini API, Cloudinary.

Primary Development Language: Python, 
Primary LLM Inference Provider: Groq, 
Development Environment: VS Code,  
Agent Orchestration: LangGraph, 
Deployment Target: Render and Nonilion
