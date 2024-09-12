import music21 as m21

from PalestrinaUTILS.scores.Score2TextConverter import Score2TextConverter


converter1 = Score2TextConverter(
    resolve_chiavetta=True,
    include_part_name=False
)

converter1.parse_database_and_save()
