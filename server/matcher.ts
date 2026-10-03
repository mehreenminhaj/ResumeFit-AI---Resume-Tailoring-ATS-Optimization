// Resume and Job Description Matching Engine with Skill Normalization and Keyword Frequency

export const SKILL_ALIASES: Record<string, string> = {
  // Languages
  'js': 'javascript',
  'javascript': 'javascript',
  'ts': 'typescript',
  'typescript': 'typescript',
  'py': 'python',
  'python': 'python',
  'golang': 'go',
  'go': 'go',
  'cpp': 'c++',
  'c++': 'c++',
  'c#': 'c#',
  'csharp': 'c#',
  
  // Frontend
  'react': 'react',
  'reactjs': 'react',
  'react.js': 'react',
  'next': 'next.js',
  'nextjs': 'next.js',
  'next.js': 'next.js',
  'vue': 'vue',
  'vuejs': 'vue',
  'vue.js': 'vue',
  'tailwind': 'tailwindcss',
  'tailwindcss': 'tailwindcss',
  'html5': 'html',
  'css3': 'css',
  
  // Backend & APIs
  'node': 'node.js',
  'nodejs': 'node.js',
  'node.js': 'node.js',
  'fastapi': 'fastapi',
  'fast-api': 'fastapi',
  'express': 'express',
  'expressjs': 'express',
  'django': 'django',
  'flask': 'flask',
  'spring': 'spring boot',
  'springboot': 'spring boot',
  'spring boot': 'spring boot',
  'rest': 'rest api',
  'restful': 'rest api',
  'rest api': 'rest api',
  'rest apis': 'rest api',
  'restful apis': 'rest api',
  'graphql': 'graphql',
  'grpc': 'grpc',
  'microservices': 'microservices',
  
  // Databases
  'postgres': 'postgresql',
  'postgresql': 'postgresql',
  'psql': 'postgresql',
  'mongo': 'mongodb',
  'mongodb': 'mongodb',
  'mysql': 'mysql',
  'sqlite': 'sqlite',
  'redis': 'redis',
  
  // Cloud & DevOps
  'aws': 'aws',
  'amazon web services': 'aws',
  'gcp': 'google cloud',
  'google cloud platform': 'google cloud',
  'google cloud': 'google cloud',
  'azure': 'azure',
  'microsoft azure': 'azure',
  'docker': 'docker',
  'k8s': 'kubernetes',
  'kubernetes': 'kubernetes',
  'ci/cd': 'ci/cd',
  'cicd': 'ci/cd',
  'terraform': 'terraform',
  'git': 'git',
  'github actions': 'github actions',
  
  // AI & Data
  'ml': 'machine learning',
  'machine learning': 'machine learning',
  'dl': 'deep learning',
  'deep learning': 'deep learning',
  'nlp': 'nlp',
  'natural language processing': 'nlp',
  'llm': 'large language models',
  'llms': 'large language models',
  'genai': 'generative ai',
  'generative ai': 'generative ai',
  'pandas': 'pandas',
  'numpy': 'numpy',
  'pytorch': 'pytorch',
  'tensorflow': 'tensorflow',
  'scikit-learn': 'scikit-learn',
  'sklearn': 'scikit-learn',
  'spacy': 'spacy',
  'rag': 'rag'
};

export function normalizeSkill(skill: string): string {
  const cleaned = skill.toLowerCase().trim().replace(/^[•\-\*\s]+/, '');
  return SKILL_ALIASES[cleaned] || cleaned;
}

export function extractKeywordFrequencies(text: string): Map<string, number> {
  const counts = new Map<string, number>();
  if (!text) return counts;

  // Match words, including terms with #, +, or . like c++, node.js, c#
  const matches = text.toLowerCase().match(/\b[a-z][a-z0-9+#.]*\b/g);
  if (!matches) return counts;

  const stopWords = new Set([
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'are', 'you', 'will',
    'our', 'team', 'work', 'your', 'about', 'join', 'opportunity', 'company', 'role',
    'looking', 'candidate', 'skills', 'experience', 'years', 'working', 'ability', 'must',
    'responsible', 'requirements', 'qualifications', 'such', 'well', 'using', 'plus',
    'strong', 'knowledge', 'understanding', 'preferred', 'across', 'including'
  ]);

  for (const word of matches) {
    const clean = word.replace(/^\.+|\.+$/g, '');
    if (clean.length > 2 && !stopWords.has(clean) && !/^\d+$/.test(clean)) {
      counts.set(clean, (counts.get(clean) || 0) + 1);
    }
  }

  return counts;
}

export function computeATSScore(
  matchedRequired: number,
  totalRequired: number,
  matchedPreferred: number,
  totalPreferred: number,
  keywordMatchPct: number,
  hasExperience: boolean
): number {
  const reqWeight = 0.50;
  const prefWeight = 0.15;
  const kwWeight = 0.25;
  const expWeight = 0.10;

  const reqScore = totalRequired > 0 ? (matchedRequired / totalRequired) * 100 : 80;
  const prefScore = totalPreferred > 0 ? (matchedPreferred / totalPreferred) * 100 : 70;
  const kwScore = Math.min(100, keywordMatchPct);
  const expScore = hasExperience ? 90 : 50;

  const total = (reqScore * reqWeight) + (prefScore * prefWeight) + (kwScore * kwWeight) + (expScore * expWeight);
  return Math.min(99, Math.max(15, Math.round(total)));
}
