// Sample Tekla macro that calls TeklaModelBuilder.ImportMembers
// Place this code inside a Tekla plugin project or run as a Tekla macro after compiling
using System;
using Tekla.Structures.Model;

namespace TeklaStructures.AIBuildX
{
    public class ImportMacro
    {
        public static void Run(string[] args)
        {
            try
            {
                var builder = new TeklaModelBuilder();
                var jsonPath = args != null && args.Length > 0 ? args[0] : "C:\\path\\to\\fully_enhanced_data.json";
                var res = builder.ImportMembers(jsonPath, "AIBuildX_Imported");
                if (res.Success)
                {
                    Console.WriteLine(res.Message);
                }
                else
                {
                    Console.WriteLine("Import failed: " + res.Message);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Macro failed: " + ex.Message);
            }
        }
    }
}
