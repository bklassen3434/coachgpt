import sqlite3
from pathlib import Path


# ------------------ Overview ------------------ #
# This script creates a SQLite database and table for storing softball data.
# It provides functionality to connect to the database, create the table, and close the connection.

class YakkerTechDB:
    def __init__(self, db_path: str = "structured/sqllite_db.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def create_table(self):
        """Create the yakkertech table with all required columns"""

        self.cursor.execute("DROP TABLE IF EXISTS yakkertech")
        
        self.cursor.execute('''
        CREATE TABLE yakkertech (
            "PitchNo" INTEGER,
            "Date" TEXT,
            "Time" TEXT,
            "PAofInning" INTEGER,
            "PitchofPA" INTEGER,
            "Pitcher" TEXT,
            "PitcherId" TEXT,
            "PitcherThrows" TEXT,
            "PitcherTeam" TEXT,
            "Batter" TEXT,
            "BatterId" TEXT,
            "BatterSide" TEXT,
            "BatterTeam" TEXT,
            "PitcherSet" FLOAT,
            "Inning" INTEGER,
            "Top/Bottom" TEXT,
            "Outs" INTEGER,
            "Balls" INTEGER,
            "Strikes" INTEGER,
            "TaggedPitchType" TEXT,
            "AutoPitchType" FLOAT,
            "PitchCall" TEXT,
            "KorBB" TEXT,
            "HitType" TEXT,
            "PlayResult" TEXT,
            "OutsOnPlay" FLOAT,
            "RunsScored" FLOAT,
            "Notes" FLOAT,
            "RelSpeed" FLOAT,
            "VertRelAngle" FLOAT,
            "HorzRelAngle" FLOAT,
            "SpinRate" FLOAT,
            "SpinAxis" FLOAT,
            "Tilt" TEXT,
            "RelHeight" FLOAT,
            "RelSide" FLOAT,
            "Extension" FLOAT,
            "VertBreak" FLOAT,
            "InducedVertBreak" FLOAT,
            "HorzBreak" FLOAT,
            "PlateLocHeight" FLOAT,
            "PlateLocSide" FLOAT,
            "ZoneSpeed" FLOAT,
            "VertApprAngle" FLOAT,
            "HorzApprAngle" FLOAT,
            "ZoneTime" FLOAT,
            "ExitSpeed" FLOAT,
            "Angle" FLOAT,
            "Direction" FLOAT,
            "HitSpinRate" FLOAT,
            "PositionAt110X" FLOAT,
            "PositionAt110Y" FLOAT,
            "PositionAt110Z" FLOAT,
            "Distance" FLOAT,
            "LastTrackedDistance" FLOAT,
            "Bearing" FLOAT,
            "HangTime" FLOAT,
            "pfxx" FLOAT,
            "pfxz" FLOAT,
            "x0" FLOAT,
            "y0" FLOAT,
            "z0" FLOAT,
            "vx0" FLOAT,
            "vy0" FLOAT,
            "vz0" FLOAT,
            "ax0" FLOAT,
            "ay0" FLOAT,
            "az0" FLOAT,
            "HomeTeam" TEXT,
            "AwayTeam" TEXT,
            "Stadium" FLOAT,
            "Level" FLOAT,
            "League" FLOAT,
            "GameID" TEXT,
            "PitchUUID" TEXT,
            "yt_RelSpeed" FLOAT,
            "yt_RelHeight" FLOAT,
            "yt_RelSide" FLOAT,
            "yt_VertRelAngle" FLOAT,
            "yt_HorzRelAngle" FLOAT,
            "yt_ZoneSpeed" FLOAT,
            "yt_PlateLocHeight" FLOAT,
            "yt_PlateLocSide" FLOAT,
            "yt_VertApprAngle" FLOAT,
            "yt_HorzApprAngle" FLOAT,
            "yt_ZoneTime" FLOAT,
            "yt_HorzBreak" FLOAT,
            "yt_InducedVertBreak" FLOAT,
            "yt_OutOfPlane" FLOAT,
            "yt_FSRI" FLOAT,
            "yt_EffectiveSpin" FLOAT,
            "yt_GyroSpin" FLOAT,
            "yt_Efficiency" FLOAT,
            "yt_SpinComponentX" FLOAT,
            "yt_SpinComponentY" FLOAT,
            "yt_SpinComponentZ" FLOAT,
            "yt_HitVelocityX" FLOAT,
            "yt_HitVelocityY" FLOAT,
            "yt_HitVelocityZ" FLOAT,
            "yt_HitLocationX" FLOAT,
            "yt_HitLocationY" FLOAT,
            "yt_HitLocationZ" FLOAT,
            "yt_GroundLocationX" FLOAT,
            "yt_GroundLocationY" FLOAT,
            "yt_HitBreakX" FLOAT,
            "yt_HitBreakY" FLOAT,
            "yt_HitBreakT" FLOAT,
            "yt_HitSpinComponentX" FLOAT,
            "yt_HitSpinComponentY" FLOAT,
            "yt_HitSpinComponentZ" FLOAT,
            "yt_SessionName" FLOAT,
            "Note" FLOAT,
            "yt_PitchSpinConfidence" FLOAT,
            "yt_PitchReleaseConfidence" FLOAT,
            "yt_HitSpinConfidence" FLOAT,
            "yt_EffectiveBattingSpeed" FLOAT,
            "yt_ReleaseAccuracy" TEXT,
            "yt_ZoneAccuracy" TEXT,
            "yt_SeamLat" FLOAT,
            "yt_SeamLong" FLOAT,
            "yt_ReleaseDistance" FLOAT,
            "Catcher" TEXT,
            "CatcherId" FLOAT,
            "CatcherTeam" TEXT,
            "yt_AeroModel" TEXT
        );
        ''')

def main():
    db = YakkerTechDB()
    db.connect()
    db.create_table()
    db.close()

if __name__ == "__main__":
    main()
