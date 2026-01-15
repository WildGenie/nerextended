using System;
using System.Collections.Generic;
using System.Linq;
using Nuve.Lang;
using Nuve.Morphologic.Structure;
using System.Text.Json;

namespace NuveWrapper
{
    class Program
    {
        static void Main(string[] args)
        {
            Language tr = LanguageFactory.Create(LanguageType.Turkish);

            // Batch mode via stdin (JSON input/output for robustness)
            string line;
            while ((line = Console.ReadLine()) != null)
            {
                if (string.IsNullOrWhiteSpace(line)) continue;
                string word = line.Trim();
                var results = AnalyzeWord(tr, word);
                Console.WriteLine(JsonSerializer.Serialize(results));
            }
        }

        static AnalysisResult AnalyzeWord(Language tr, string word)
        {
            try
            {
                IList<Word> solutions = tr.Analyze(word);
                var analyses = new List<DetailedAnalysis>();

                foreach (var sol in solutions)
                {
                    var morphemeDetails = new List<MorphemeDetail>();
                    foreach (var allomorph in sol)
                    {
                        var m = allomorph.Morpheme;
                        morphemeDetails.Add(new MorphemeDetail
                        {
                            Surface = allomorph.Surface,
                            LexicalForm = m.LexicalForm,
                            Id = m.Id,
                            Type = m.Type.ToString(),
                            Labels = m.Labels.ToList(),
                            HasChange = allomorph.Surface != m.LexicalForm
                        });
                    }

                    analyses.Add(new DetailedAnalysis
                    {
                        Stem = sol.GetStem().GetSurface(),
                        Morphemes = morphemeDetails
                    });
                }

                return new AnalysisResult
                {
                    Word = word,
                    Analyses = analyses
                };
            }
            catch (Exception ex)
            {
                return new AnalysisResult
                {
                    Word = word,
                    Error = ex.Message
                };
            }
        }
    }

    public class AnalysisResult
    {
        public string Word { get; set; }
        public List<DetailedAnalysis> Analyses { get; set; } = new List<DetailedAnalysis>();
        public string Error { get; set; }
    }

    public class DetailedAnalysis
    {
        public string Stem { get; set; }
        public List<MorphemeDetail> Morphemes { get; set; } = new List<MorphemeDetail>();
    }

    public class MorphemeDetail
    {
        public string Surface { get; set; }
        public string LexicalForm { get; set; }
        public string Id { get; set; }
        public string Type { get; set; }
        public List<string> Labels { get; set; }
        public bool HasChange { get; set; }
    }
}
