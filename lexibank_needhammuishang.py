import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language, Lexeme
from pylexibank import FormSpec


@attr.s
class CustomLanguage(Language):
    Location = attr.ib(default=None)
    Remark = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    Orthographic_Entry = attr.ib(default=None)
    Attestation = attr.ib(default=None, type=int)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "needhammuishaung"
    language_class = CustomLanguage
    lexeme_class = CustomLexeme
    form_spec = FormSpec(separators="~;,/", missing_data=["∅"],
                         first_form_only=False,
                         replacements=[(" ", "_")])

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # add concept
        concepts = {}
        for concept in self.concepts:
            idx = concept["NUMBER"] + "_" + slug(concept["GLOSS"])
            args.writer.add_concept(
                    ID=idx,
                    Name=concept["GLOSS"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"]
                    )
            concepts[concept["NUMBER"]] = idx # lookup key
        args.log.info("added concepts")

        # add language
        args.writer.add_languages()
        args.log.info("added languages")

        # read in data
        data = self.raw_dir.read_csv(
            "Needham-1897-264.tsv", delimiter="\t", dicts=True
        )
        # add data
        for entry in pb(data, desc="cldfify", total=len(data)):
            args.writer.add_forms_from_value(
                Language_ID="MuishaungNeedham",
                Parameter_ID=concepts[entry["NUMBER"]],
                Orthographic_Entry=entry["ORTH_NEEDHAM"],
                Value=entry["PHON_NEEDHAM"],
                Source=["Needham1897"],
                Attestation=1897
            )
            if entry["PHON_MODERN"].strip() and entry["PHON_MODERN"] not in ["--"]:
                args.writer.add_forms_from_value(
                    Language_ID="MuishaungModern",
                    Parameter_ID=concepts[entry["NUMBER"]],
                    Orthographic_Entry=entry["ROMAN_MODERN"],
                    Value=entry["PHON_MODERN"],
                    Source="VanDam2025",
                    Attestation=2024
                    )
