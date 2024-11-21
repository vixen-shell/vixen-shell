import re, locale
from abc import ABC, abstractmethod
from typing import Union


class LocaleType(str):
    """
    Represents a locale as a string.
    Example: 'en-US', 'fr-FR'.
    """

    pass


class AbsLocales(ABC):
    @abstractmethod
    def get(self, locale: str, data: list[Union[str | int | float]] = []):
        pass

    @abstractmethod
    def from_scratch(self, default: str, locales: dict[LocaleType, str]):
        pass


def get_locales_reference(feature_name: str):
    class LocalesReference(AbsLocales):
        def get(self, locale: str, data: list[str | int | float] = []):
            from vx_features import RootContents

            template = (
                RootContents(feature_name)
                .get("data", "__locales__")
                .get(locale, locale)
            )

            def replace_data(match):
                index = int(match.group(1))
                return str(data[index]) if index < len(data) else match.group(0)

            return re.sub(r"\[(\d+)\]", replace_data, template)

        def from_scratch(self, default: str, locales: dict[LocaleType, str]):
            return locales.get(locale.getlocale()[0]) or default

    return LocalesReference()
