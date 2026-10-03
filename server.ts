import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import mammoth from 'mammoth';
import {
  analyzeJobDescription,
  analyzeResume,
  computeMatchAnalysis,
  generateTailoredResume,
  rewriteBulletOptions,
} from './server/gemini.js';
import { generateDocxResume } from './server/docx-generator.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;

app.use(express.json({ limit: '25mb' }));

// Helper to safely parse PDF buffer
async function extractTextFromPdf(buffer: Buffer): Promise<string> {
  try {
    const pdfModule = await import('pdf-parse');
    const pdfParse = (pdfModule as any).default || pdfModule;
    const parsed = await pdfParse(buffer);
    return parsed.text || '';
  } catch (err) {
    console.error('PDF parsing error:', err);
    // Fallback: extract plain ascii strings
    const str = buffer.toString('binary');
    const ascii = str.replace(/[^\x20-\x7E\n\r\t]/g, ' ');
    return ascii.replace(/\s+/g, ' ').slice(0, 8000);
  }
}

// Helper to safely parse DOCX buffer
async function extractTextFromDocx(buffer: Buffer): Promise<string> {
  try {
    const result = await mammoth.extractRawText({ buffer });
    return result.value || '';
  } catch (err) {
    console.error('DOCX parsing error:', err);
    throw new Error('Failed to parse DOCX document');
  }
}

/**
 * Health check
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

/**
 * POST /api/parse-document
 * Expects { filename: string, base64: string } or { text: string }
 */
app.post('/api/parse-document', async (req, res) => {
  try {
    const { filename, base64, text } = req.body;

    if (text && typeof text === 'string') {
      return res.json({ text: text.trim(), filename: filename || 'resume.txt' });
    }

    if (!base64 || typeof base64 !== 'string') {
      return res.status(400).json({ error: 'No file data or text provided.' });
    }

    const cleanBase64 = base64.replace(/^data:[^;]+;base64,/, '');
    const buffer = Buffer.from(cleanBase64, 'base64');
    const ext = (filename ? path.extname(filename).toLowerCase() : '') || '.pdf';

    let extractedText = '';

    if (ext === '.pdf') {
      extractedText = await extractTextFromPdf(buffer);
    } else if (ext === '.docx') {
      extractedText = await extractTextFromDocx(buffer);
    } else if (ext === '.txt' || ext === '.md') {
      extractedText = buffer.toString('utf-8');
    } else {
      // Try PDF first, then DOCX
      try {
        extractedText = await extractTextFromPdf(buffer);
      } catch {
        extractedText = await extractTextFromDocx(buffer);
      }
    }

    if (!extractedText || extractedText.trim().length === 0) {
      return res.status(422).json({
        error: 'Could not extract readable text from document. Please ensure it is not scanned or password-protected.',
      });
    }

    return res.json({
      filename: filename || 'resume.pdf',
      text: extractedText.trim(),
      characterCount: extractedText.length,
    });
  } catch (err: any) {
    console.error('Document parsing error:', err);
    return res.status(500).json({ error: err.message || 'Internal error parsing file' });
  }
});

/**
 * POST /api/fetch-url
 * Fetches Job Description from a URL
 */
app.post('/api/fetch-url', async (req, res) => {
  try {
    const { url } = req.body;
    if (!url || typeof url !== 'string') {
      return res.status(400).json({ error: 'Valid URL is required.' });
    }

    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    });

    if (!response.ok) {
      return res.status(response.status).json({
        error: `Failed to fetch page (HTTP ${response.status}). Many job portals require copy-pasting the text directly.`,
      });
    }

    const html = await response.text();

    // Strip scripts, styles, tags to extract readable content
    let text = html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, ' ')
      .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, ' ')
      .replace(/<nav\b[^<]*(?:(?!<\/nav>)<[^<]*)*<\/nav>/gi, ' ')
      .replace(/<footer\b[^<]*(?:(?!<\/footer>)<[^<]*)*<\/footer>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&#39;/g, "'")
      .replace(/&quot;/g, '"')
      .replace(/\s+/g, ' ')
      .trim();

    if (text.length > 8000) {
      text = text.slice(0, 8000);
    }

    return res.json({ text, url });
  } catch (err: any) {
    console.error('URL Fetch error:', err);
    return res.status(500).json({
      error: 'Unable to reach URL. Please copy and paste the job description text manually.',
    });
  }
});

/**
 * POST /api/analyze-jd
 */
app.post('/api/analyze-jd', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text || text.trim().length < 20) {
      return res.status(400).json({ error: 'Job description text must be at least 20 characters.' });
    }
    const jdData = await analyzeJobDescription(text);
    return res.json(jdData);
  } catch (err: any) {
    console.error('Error in /api/analyze-jd:', err);
    return res.status(500).json({ error: err.message || 'Failed to analyze job description' });
  }
});

/**
 * POST /api/analyze-resume
 */
app.post('/api/analyze-resume', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text || text.trim().length < 20) {
      return res.status(400).json({ error: 'Resume text must be at least 20 characters.' });
    }
    const resumeData = await analyzeResume(text);
    return res.json(resumeData);
  } catch (err: any) {
    console.error('Error in /api/analyze-resume:', err);
    return res.status(500).json({ error: err.message || 'Failed to analyze resume' });
  }
});

/**
 * POST /api/full-analysis
 * Orchestrates:
 * 1. Takes resume text (or structured ResumeData)
 * 2. Takes JD text (or structured JobDescriptionData)
 * 3. Runs extraction if needed
 * 4. Runs deterministic + semantic match
 */
app.post('/api/full-analysis', async (req, res) => {
  try {
    const { resumeText, jdText, resumeData: existingResume, jdData: existingJd } = req.body;

    let resume = existingResume;
    if (!resume) {
      if (!resumeText) return res.status(400).json({ error: 'Missing resume text or data.' });
      resume = await analyzeResume(resumeText);
    }

    let jd = existingJd;
    if (!jd) {
      if (!jdText) return res.status(400).json({ error: 'Missing job description text or data.' });
      jd = await analyzeJobDescription(jdText);
    }

    const matchAnalysis = await computeMatchAnalysis(resume, jd);

    return res.json({
      resume,
      jd,
      analysis: matchAnalysis,
    });
  } catch (err: any) {
    console.error('Error in /api/full-analysis:', err);
    return res.status(500).json({ error: err.message || 'Failed to complete match analysis' });
  }
});

/**
 * POST /api/tailor
 * Generates tailored resume while strictly obeying anti-hallucination rules
 */
app.post('/api/tailor', async (req, res) => {
  try {
    const { resume, jd, analysis } = req.body;
    if (!resume || !jd || !analysis) {
      return res.status(400).json({ error: 'resume, jd, and analysis objects are required.' });
    }

    const tailored = await generateTailoredResume(resume, jd, analysis);
    return res.json(tailored);
  } catch (err: any) {
    console.error('Error in /api/tailor:', err);
    return res.status(500).json({ error: err.message || 'Failed to generate tailored resume' });
  }
});

/**
 * POST /api/rewrite-bullet
 * Generates 3 truthful bullet options for a specific bullet point
 */
app.post('/api/rewrite-bullet', async (req, res) => {
  try {
    const { bullet, role, jdKeywords } = req.body;
    if (!bullet) {
      return res.status(400).json({ error: 'bullet text is required.' });
    }

    const result = await rewriteBulletOptions(bullet, role || 'Professional', jdKeywords || []);
    return res.json(result);
  } catch (err: any) {
    console.error('Error in /api/rewrite-bullet:', err);
    return res.status(500).json({ error: err.message || 'Failed to rewrite bullet' });
  }
});

/**
 * POST /api/export-docx
 * Generates and downloads a genuine .docx file
 */
app.post('/api/export-docx', async (req, res) => {
  try {
    const { resume, tailored } = req.body;
    if (!resume || !tailored) {
      return res.status(400).json({ error: 'resume and tailored data are required for DOCX export.' });
    }

    const buffer = await generateDocxResume(resume, tailored);

    const safeName = (resume.fullName || 'Candidate')
      .replace(/[^a-zA-Z0-9_-]/g, '_')
      .toLowerCase();
    const filename = `${safeName}_tailored_resume.docx`;

    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Length', buffer.length);
    return res.send(buffer);
  } catch (err: any) {
    console.error('Error in /api/export-docx:', err);
    return res.status(500).json({ error: err.message || 'Failed to generate Word document' });
  }
});

// Mount Vite middleware in development, or serve dist in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.resolve(__dirname, 'dist')));
  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
  });
} else {
  const { createServer: createViteServer } = await import('vite');
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });
  app.use(vite.middlewares);
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`ResumeFit AI Server listening on http://0.0.0.0:${PORT}`);
});
