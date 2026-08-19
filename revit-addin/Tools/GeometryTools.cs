using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace RevitBridge.Tools
{
    /// <summary>
    /// Implementações concretas das tools que tocam a Revit API. Espelham os
    /// nomes/schemas definidos em backend/app/agent/tools.py.
    /// </summary>
    public static class GeometryTools
    {
        private static Document GetActiveDoc(UIApplication app) => app.ActiveUIDocument.Document;

        public static object GetLevels(UIApplication app)
        {
            var doc = GetActiveDoc(app);
            var levels = new FilteredElementCollector(doc)
                .OfClass(typeof(Level))
                .Cast<Level>()
                .OrderBy(l => l.Elevation)
                .Select(l => new
                {
                    id = l.Id.IntegerValue,
                    name = l.Name,
                    elevation_ft = l.Elevation,
                    elevation_m = UnitUtils.ConvertFromInternalUnits(l.Elevation, UnitTypeId.Meters),
                })
                .ToList();

            return new { levels };
        }

        public static object CreateWall(UIApplication app, JsonElement input)
        {
            var doc = GetActiveDoc(app);

            string levelName = input.GetProperty("level").GetString() ?? "";
            var level = FindLevel(doc, levelName);
            if (level == null)
                return new { error = "level_not_found", level = levelName };

            var start = input.GetProperty("start");
            var end = input.GetProperty("end");
            double heightM = input.GetProperty("height").GetDouble();
            string? wallTypeName = input.TryGetProperty("wall_type", out var wt) ? wt.GetString() : null;

            XYZ p1 = MetersToXyz(start.GetProperty("x").GetDouble(), start.GetProperty("y").GetDouble());
            XYZ p2 = MetersToXyz(end.GetProperty("x").GetDouble(), end.GetProperty("y").GetDouble());
            double heightFt = UnitUtils.ConvertToInternalUnits(heightM, UnitTypeId.Meters);

            var wallType = FindWallType(doc, wallTypeName);

            using var tx = new Transaction(doc, "Revit AI: Criar Parede");
            tx.Start();
            var wall = Wall.Create(doc, Line.CreateBound(p1, p2), wallType?.Id ?? doc.GetDefaultElementTypeId(ElementTypeGroup.WallType), level.Id, heightFt, 0, false, false);
            tx.Commit();

            return new { created = true, wall_id = wall.Id.IntegerValue };
        }

        public static object CreateRoom(UIApplication app, JsonElement input)
        {
            var doc = GetActiveDoc(app);

            string levelName = input.GetProperty("level").GetString() ?? "";
            var level = FindLevel(doc, levelName);
            if (level == null)
                return new { error = "level_not_found", level = levelName };

            var point = input.GetProperty("point");
            XYZ p = MetersToXyz(point.GetProperty("x").GetDouble(), point.GetProperty("y").GetDouble());
            string? name = input.TryGetProperty("name", out var n) ? n.GetString() : null;

            using var tx = new Transaction(doc, "Revit AI: Criar Ambiente");
            tx.Start();
            var room = doc.Create.NewRoom(level, new UV(p.X, p.Y));
            if (room != null && !string.IsNullOrWhiteSpace(name))
                room.get_Parameter(BuiltInParameter.ROOM_NAME)?.Set(name);
            tx.Commit();

            return new { created = room != null, room_id = room?.Id.IntegerValue };
        }

        private static Level? FindLevel(Document doc, string name) =>
            new FilteredElementCollector(doc)
                .OfClass(typeof(Level))
                .Cast<Level>()
                .FirstOrDefault(l => l.Name.Equals(name, System.StringComparison.OrdinalIgnoreCase));

        private static WallType? FindWallType(Document doc, string? name)
        {
            if (string.IsNullOrWhiteSpace(name)) return null;
            return new FilteredElementCollector(doc)
                .OfClass(typeof(WallType))
                .Cast<WallType>()
                .FirstOrDefault(w => w.Name.Equals(name, System.StringComparison.OrdinalIgnoreCase));
        }

        private static XYZ MetersToXyz(double xMeters, double yMeters) => new XYZ(
            UnitUtils.ConvertToInternalUnits(xMeters, UnitTypeId.Meters),
            UnitUtils.ConvertToInternalUnits(yMeters, UnitTypeId.Meters),
            0);
    }
}
