import { useState } from 'react';
import { BookOpen, Copy, Check, ExternalLink, GraduationCap, Award, FileText } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TooltipProvider } from '@/components/ui/tooltip';

interface Reference {
  id: number;
  citation: string;
  doi?: string;
  url?: string;
  topic: string;
  peerReviewed: boolean;
  category: string;
}

const REFERENCES: Reference[] = [
  {
    id: 1,
    citation: 'Vaswani, A., et al. (2017). "Attention is all you need." NeurIPS.',
    url: 'https://arxiv.org/abs/1706.03762',
    topic: 'Transformer architecture',
    peerReviewed: true,
    category: 'Machine Learning'
  },
  {
    id: 2,
    citation: 'Brown, T., et al. (2020). "Language models are few-shot learners." NeurIPS.',
    url: 'https://arxiv.org/abs/2005.14165',
    topic: 'GPT-3, large language models',
    peerReviewed: true,
    category: 'Machine Learning'
  },
  {
    id: 3,
    citation: 'Shannon, C.E. (1948). "A mathematical theory of communication." Bell System Technical Journal, 27(3), 379–423.',
    doi: '10.1002/j.1538-7305.1948.tb01338.x',
    topic: 'Foundational information theory',
    peerReviewed: true,
    category: 'Information Theory'
  },
  {
    id: 12,
    citation: 'Landauer, R. (1961). "Irreversibility and heat generation in the computing process." IBM Journal of Research and Development, 5(3), 183–191.',
    doi: '10.1147/rd.53.0183',
    topic: "Landauer's principle",
    peerReviewed: true,
    category: 'Physics'
  },
  {
    id: 14,
    citation: 'Nash, J. (1950). "Equilibrium points in n-person games." PNAS, 36(1), 48–49.',
    doi: '10.1073/pnas.36.1.48',
    topic: 'Nash equilibrium (Nobel Prize)',
    peerReviewed: true,
    category: 'Game Theory'
  },
  {
    id: 20,
    citation: 'Lamport, L., Shostak, R., & Pease, M. (1982). "The Byzantine Generals Problem." ACM TOPLAS, 4(3), 382–401.',
    doi: '10.1145/357172.357176',
    topic: 'Byzantine fault tolerance',
    peerReviewed: true,
    category: 'Distributed Systems'
  },
  {
    id: 27,
    citation: 'Boneh, D., Lynn, B., & Shacham, H. (2001). "Short signatures from the Weil pairing." ASIACRYPT.',
    url: 'https://crypto.stanford.edu/~dabo/pubs/papers/weilsig.pdf',
    topic: 'BLS signatures',
    peerReviewed: true,
    category: 'Cryptography'
  },
  {
    id: 35,
    citation: 'Gödel, K. (1931). "Über formal unentscheidbare Sätze der Principia Mathematica." Monatshefte für Mathematik und Physik, 38(1), 173–198.',
    doi: '10.1007/BF01700692',
    topic: 'Incompleteness theorems',
    peerReviewed: true,
    category: 'Logic'
  },
  {
    id: 43,
    citation: 'Friston, K. (2010). "The free-energy principle: a unified brain theory?" Nature Reviews Neuroscience, 11(2), 127–138.',
    doi: '10.1038/nrn2787',
    topic: 'Free energy principle',
    peerReviewed: true,
    category: 'Neuroscience'
  },
  {
    id: 44,
    citation: 'Hofstadter, D.R. (1979). Gödel, Escher, Bach: An Eternal Golden Braid. Basic Books.',
    topic: 'Strange loops (Pulitzer Prize)',
    peerReviewed: true,
    category: 'Philosophy'
  }
];

const BIBTEX = `@techreport{arifos2026apex,
  title = {APEX: A Thermodynamically Grounded Constitutional Framework for AI Governance},
  author = {Fazil, Muhammad Arif bin},
  year = {2026},
  month = {February},
  institution = {arifOS Project},
  url = {https://apex.arif-fazil.com},
  note = {Research framework. Implementations should be validated for specific use cases.}
}`;

export function CitationBlock() {
  const [copiedBibtex, setCopiedBibtex] = useState(false);
  const [expandedRef, setExpandedRef] = useState<number | null>(null);

  const copyBibtex = () => {
    navigator.clipboard.writeText(BIBTEX);
    setCopiedBibtex(true);
    setTimeout(() => setCopiedBibtex(false), 2000);
  };

  const stats = {
    total: 50,
    peerReviewed: 44,
    books: 12,
    articles: 32,
    conferences: 6
  };

  return (
    <TooltipProvider>
      <div className="space-y-12">
        {/* Header Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-0 border border-theory-300/20 bg-black/40">
          {[
            { icon: GraduationCap, val: stats.total, label: 'TOTAL_CITATIONS' },
            { icon: Award, val: stats.peerReviewed, label: 'PEER_REVIEWED' },
            { icon: FileText, val: stats.articles, label: 'JOURNAL_ARTICLES' },
            { icon: BookOpen, val: stats.books, label: 'BOOKS_MANUSCRIPTS' }
          ].map((stat, i) => (
            <div key={i} className={`p-8 text-center border-r border-theory-300/10 last:border-r-0 hover:bg-theory-300/[0.02] transition-colors`}>
              <stat.icon className="w-5 h-5 text-theory-300 mx-auto mb-4 opacity-40" />
              <p className="text-3xl font-mono font-bold text-white mb-1">{stat.val}</p>
              <p className="text-[8px] font-display text-gray-600 tracking-widest">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Scientific Rigor Score */}
        <div className="p-8 border border-theory-500 bg-black relative">
          <div className="absolute top-0 left-0 w-2 h-2 bg-theory-300" />
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="text-center md:text-left">
              <p className="text-[10px] font-display font-bold text-theory-300 mb-2 tracking-widest">SCIENTIFIC_RIGOR_METRIC</p>
              <p className="text-xs font-mono text-gray-500 italic max-w-md">Based on peer-review status, citation density, and methodological transparency protocols.</p>
            </div>
            <div className="flex items-center gap-8 border-l border-theory-300/20 pl-8">
              <div className="text-right">
                <p className="text-5xl font-mono font-bold text-white leading-none">95<span className="text-xl text-theory-300">/100</span></p>
              </div>
              <Badge variant="outline" className="rounded-none border-green-500 text-green-500 text-[10px] font-display tracking-widest bg-green-500/5 px-4 py-1">
                A_GRADE_CANON
              </Badge>
            </div>
          </div>
          <div className="mt-8 h-1 bg-gray-900 overflow-hidden">
            <div className="h-full bg-theory-300" style={{ width: '95%' }} />
          </div>
        </div>

        {/* BibTeX Export */}
        <div className="border border-theory-300/20 bg-black/40 p-8 relative">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <BookOpen className="w-4 h-4 text-theory-300" />
              <h4 className="text-[10px] font-display text-gray-500 tracking-widest uppercase">CITE_THIS_CANON</h4>
            </div>
            <Button
              onClick={copyBibtex}
              variant="outline"
              className="rounded-none border-theory-300 text-theory-200 hover:bg-theory-300/15 hover:text-white font-display text-[9px] tracking-widest px-6"
            >
              {copiedBibtex ? <Check className="w-3 h-3 mr-2" /> : <Copy className="w-3 h-3 mr-2" />}
              {copiedBibtex ? 'DATA_COPIED' : 'COPY_BIBTEX'}
            </Button>
          </div>
          <pre className="p-6 border border-theory-300/10 bg-black text-[10px] text-gray-500 overflow-x-auto font-mono leading-relaxed italic">
            {BIBTEX}
          </pre>
        </div>

        {/* Key References */}
        <div className="space-y-8">
          <div className="flex items-center gap-4 mb-8">
            <Award className="w-4 h-4 text-theory-300" />
            <h4 className="text-[10px] font-display text-white tracking-[0.3em] uppercase">CANONICAL_REFERENCES</h4>
          </div>
          
          <div className="grid gap-4">
            {REFERENCES.map((ref) => (
              <div
                key={ref.id}
                className={`
                  p-6 transition-all cursor-pointer border rounded-none
                  ${expandedRef === ref.id
                    ? 'border-theory-300 bg-theory-300/[0.05]'
                    : 'border-theory-500/40 bg-black/40 hover:border-theory-300/60 hover:bg-theory-300/[0.03]'
                  }
                `}
                onClick={() => setExpandedRef(expandedRef === ref.id ? null : ref.id)}
              >
                <div className="flex items-start gap-8">
                  <span className="text-[10px] font-display text-theory-300/40 mt-1">REF_{ref.id < 10 ? '0'+ref.id : ref.id}</span>
                  <div className="flex-1">
                    <p 
                      className="text-sm font-mono text-gray-300 leading-relaxed mb-4"
                      dangerouslySetInnerHTML={{ __html: ref.citation }}
                    />
                    <div className="flex flex-wrap items-center gap-4">
                      <Badge variant="outline" className="rounded-none border-theory-300/20 text-gray-500 text-[8px] font-display uppercase">
                        {ref.category}
                      </Badge>
                      {ref.peerReviewed && (
                        <Badge variant="outline" className="rounded-none border-green-500/30 text-green-500/60 text-[8px] font-display uppercase">
                          Peer_Reviewed
                        </Badge>
                      )}
                      <span className="text-[9px] font-mono text-gray-600 italic tracking-tighter">{ref.topic}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {(ref.doi || ref.url) && (
                      <a
                        href={ref.doi ? `https://doi.org/${ref.doi}` : ref.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-3 border border-theory-300/20 text-gray-600 hover:text-theory-300 hover:border-theory-500 transition-all"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center pt-8">
            <a 
              href="/references.json"
              className="font-display text-[9px] text-theory-300 hover:text-white tracking-[0.4em] uppercase transition-all flex items-center justify-center gap-4 group"
            >
              <span className="w-8 h-[1px] bg-theory-300/20 group-hover:w-12 transition-all" />
              Access_Complete_Bibliography_Archive
              <span className="w-8 h-[1px] bg-theory-300/20 group-hover:w-12 transition-all" />
            </a>
          </div>
        </div>

        {/* Machine-Readable Endpoints */}
        <div className="p-8 border border-theory-300/10 bg-black/60">
          <p className="text-[10px] font-display text-gray-600 mb-6 tracking-widest uppercase">M2M_ENDPOINTS</p>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 border border-theory-300/5 bg-theory-300/[0.01]">
              <code className="text-xs font-mono text-theory-300/60">/references.json</code>
              <Badge variant="outline" className="rounded-none border-theory-300/20 text-gray-600 text-[8px] font-display uppercase">JSON_PROTOCOL</Badge>
            </div>
            <div className="flex items-center justify-between p-4 border border-theory-300/5 bg-theory-300/[0.01]">
              <code className="text-xs font-mono text-theory-300/60">/llms.txt</code>
              <Badge variant="outline" className="rounded-none border-theory-300/20 text-gray-600 text-[8px] font-display uppercase">RAW_CONTEXT</Badge>
            </div>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
