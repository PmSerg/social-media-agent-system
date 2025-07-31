# Create Content Post Workflow

## Overview
Workflow for creating social media content posts with research and copywriting.

## Parameters
- **topic** (required): The subject to create content about
- **platform** (optional): Target platform (Twitter, LinkedIn, Instagram). Default: Twitter
- **tone** (optional): Content tone (professional, casual, humorous, educational). Default: professional
- **include_hashtags** (optional): Whether to include hashtags. Default: true
- **max_length** (optional): Maximum character length. Default: platform-specific

## Workflow Steps

### Step 1: Initial Validation
**Agent**: TaskMonitor
**Action**: Validate parameters and create execution plan
**Webhook Event**: `workflow_started`
```json
{
  "step": "validation",
  "status": "processing",
  "message": "Validating parameters and creating execution plan"
}
```

### Step 2: Topic Research
**Agent**: ResearchAgent
**Action**: Research the topic using web search and analysis
**Duration**: 15-30 seconds
**Webhook Event**: `research_started`
```json
{
  "step": "research",
  "status": "processing", 
  "message": "Researching topic: {topic}"
}
```

**Tools Used**:
- Web search for recent information
- Content analysis for key themes
- Trend identification

**Output**:
- Summary of findings
- Key points to include
- Relevant statistics/facts
- Current trends
- Suggested angles

**Webhook Event**: `research_completed`
```json
{
  "step": "research",
  "status": "completed",
  "data": {
    "summary": "...",
    "key_findings": ["..."],
    "trends": ["..."]
  }
}
```

### Step 3: Content Generation
**Agent**: CopywriterAgent
**Action**: Generate platform-optimized content
**Duration**: 10-20 seconds
**Webhook Event**: `content_generation_started`
```json
{
  "step": "content_generation",
  "status": "processing",
  "message": "Creating {platform} content with {tone} tone"
}
```

**Process**:
1. Analyze research findings
2. Apply platform best practices
3. Incorporate tone requirements
4. Optimize for engagement
5. Add hashtags if requested

**Platform Specifications**:
- **Twitter**: 280 characters, 3-5 hashtags
- **LinkedIn**: 1300 characters, professional tone, 5-10 hashtags
- **Instagram**: 2200 characters, emoji-friendly, 10-30 hashtags

**Output**:
- Main content text
- Hashtags (if requested)
- Engagement tips
- Alternative versions (optional)

**Webhook Event**: `content_generated`
```json
{
  "step": "content_generation",
  "status": "completed",
  "data": {
    "content": "...",
    "hashtags": ["..."],
    "character_count": 250,
    "alternatives": ["..."]
  }
}
```

### Step 4: Final Review
**Agent**: TaskMonitor
**Action**: Compile results and update Notion
**Webhook Event**: `workflow_completed`
```json
{
  "step": "final_review",
  "status": "completed",
  "summary": {
    "research_summary": "...",
    "content": "...",
    "hashtags": ["..."],
    "execution_time": 45
  }
}
```

## Error Handling

### Research Failure
**Webhook Event**: `research_error`
```json
{
  "step": "research",
  "status": "error",
  "error": "Failed to gather research data",
  "fallback": "Using general knowledge base"
}
```
**Action**: Proceed with general knowledge, notify user of limitation

### Content Generation Failure
**Webhook Event**: `content_error`
```json
{
  "step": "content_generation",
  "status": "error",
  "error": "Failed to generate content",
  "retry_attempt": 1
}
```
**Action**: Retry with adjusted parameters, fallback to simple format

### Timeout
**Maximum Duration**: 60 seconds
**Webhook Event**: `workflow_timeout`
```json
{
  "step": "current_step",
  "status": "timeout",
  "message": "Workflow exceeded time limit"
}
```

## Success Criteria
- Research completed with at least 3 key findings
- Content generated within platform limits
- All webhook notifications sent
- Notion task updated with results

## Example Execution

**Input**:
```
/create-content-post topic:"AI in Healthcare" platform:LinkedIn tone:professional
```

**Expected Timeline**:
1. 0s: Workflow started
2. 2s: Research started
3. 20s: Research completed
4. 22s: Content generation started
5. 35s: Content generated
6. 37s: Workflow completed

**Total Duration**: ~40 seconds