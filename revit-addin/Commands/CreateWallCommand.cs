using System.Linq;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace RevitBridge.Commands
{
    /// <summary>
    /// Comando de exemplo acionável manualmente pela faixa de opções do Revit
    /// (útil para testar a criação de parede sem depender do backend Python).
    /// Para registrar um botão na ribbon, adicione a chamada correspondente em
    /// App.OnStartup usando RibbonPanel.AddItem(new PushButtonData(...)).
    /// </summary>
    [Transaction(TransactionMode.Manual)]
    public class CreateWallCommand : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            var uiDoc = commandData.Application.ActiveUIDocument;
            var doc = uiDoc.Document;

            var level = new FilteredElementCollector(doc)
                .OfClass(typeof(Level))
                .Cast<Level>()
                .FirstOrDefault();

            if (level == null)
            {
                message = "Nenhum nível encontrado no projeto.";
                return Result.Failed;
            }

            using var tx = new Transaction(doc, "Revit AI: Parede de teste");
            tx.Start();
            Wall.Create(
                doc,
                Line.CreateBound(new XYZ(0, 0, 0), new XYZ(10, 0, 0)),
                level.Id,
                false);
            tx.Commit();

            return Result.Succeeded;
        }
    }
}
