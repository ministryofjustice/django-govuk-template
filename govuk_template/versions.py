import functools
import re

# TODO: make this an external package


def parse_int(name, value, loose=False):
    if not loose and value.startswith('0') and value != '0':
        raise ValueError('%s has leading zeros' % name)
    value = int(value)
    if value < 0:
        raise ValueError('%s is not a natural number' % name)
    return value


def compare_identifiers(a, b, comparator='__eq__'):
    if not a and b:
        return comparator in ('__gt__', '__ge__')
    if a and not b:
        return comparator in ('__lt__', '__le__')
    a_converted = tuple(int(i) if i.isdigit() else i for i in a)
    b_converted = tuple(int(i) if i.isdigit() else i for i in b)
    try:
        return getattr(a_converted, comparator)(b_converted)
    except TypeError:
        return getattr(a, comparator)(b)


@functools.total_ordering  # for stable sorting of versions
class Version:
    """
    Implements node-js style of semantic versioning
    https://docs.npmjs.com/misc/semver
    http://semver.org/spec/v2.0.0.html
    """

    @classmethod
    def from_tuple(cls, version):
        if not isinstance(version, (tuple, list)):
            raise ValueError('Invalid version tuple')
        if len(version) == 3:
            return cls('%s.%s.%s' % version)
        if len(version) == 4:
            return cls('%s.%s.%s-%s' % version)
        if len(version) == 5:
            if version[3] is None and version[4] is None:
                return cls('%s.%s.%s' % version[:3])
            if version[4] is None:
                return cls('%s.%s.%s-%s' % version[:4])
            if version[3] is None:
                return cls('{0}.{1}.{2}+{4}'.format(*version))
            return cls('%s.%s.%s-%s+%s' % version)
        raise ValueError('Invalid version tuple')

    def __init__(self, version, loose=False):
        self.version = version
        self.major = None
        self.minor = None
        self.patch = None
        self.pre_release = None
        self.build = None
        self.loose = loose
        self._parse()

    def _parse(self):
        v = self.version
        if not isinstance(v, str):
            raise ValueError('Invalid version %r' % v)
        if not v:
            raise ValueError('Empty version')
        if self.loose:
            v = v.lstrip()
            if v[0] in ('v', '='):
                v = v[1:].lstrip()
        matches = re.match(r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<etc>.*)$', v)
        if not matches:
            raise ValueError('%s does not contain numeric major, minor and patch versions' % self.version)
        self.major = parse_int('major', matches.group('major'), loose=self.loose)
        self.minor = parse_int('minor', matches.group('minor'), loose=self.loose)
        self.patch = parse_int('patch', matches.group('patch'), loose=self.loose)

        etc = matches.group('etc')  # type: str
        if not etc:
            return
        self._parse_etc(etc)

    def _parse_etc(self, etc):
        identifier = re.compile(r'^[0-9A-Za-z-]+$')
        invalid_numeric_identifier = re.compile(r'^0\d+$')
        if self.loose and not etc.startswith('-') and not etc.startswith('+'):
            etc = '-' + etc
        if etc.startswith('-'):
            etc = etc[1:]
            if '+' in etc:
                pos = etc.index('+')
                self.pre_release, etc = etc[:pos], etc[pos:]
            else:
                self.pre_release, etc = etc, ''
            if not self.pre_release or \
                    not all(identifier.match(part) for part in self.pre_release_identifiers) or \
                    (not self.loose and any(
                        invalid_numeric_identifier.match(part) for part in self.pre_release_identifiers
                    )):
                raise ValueError('pre-release version %s is invalid in %s' % (self.pre_release, self.version))
        if etc.startswith('+'):
            self.build = etc[1:]
            if not self.build or not all(identifier.match(part) for part in self.build_identifiers):
                raise ValueError('build version %s is invalid in %s' % (self.build, self.version))
        elif etc:
            raise ValueError('Invalid version %s' % self.version)

    def __str__(self):
        return self.version

    @property
    def normalised(self):
        if self.pre_release and self.build:
            return '%d.%d.%d-%s+%s' % (self.major, self.minor, self.patch, self.pre_release, self.build)
        if self.pre_release:
            return '%d.%d.%d-%s' % (self.major, self.minor, self.patch, self.pre_release)
        if self.build:
            return '%d.%d.%d+%s' % (self.major, self.minor, self.patch, self.build)
        return '%d.%d.%d' % (self.major, self.minor, self.patch)

    def __repr__(self):
        return '<Version %s>' % self

    @property
    def is_stable(self):
        return self.major > 0

    @property
    def pre_release_identifiers(self):
        return self.pre_release.split('.') if self.pre_release else []

    @property
    def build_identifiers(self):
        return self.build.split('.') if self.build else []

    def increment(self, level):
        if level == 'major':
            if self.pre_release and self.patch == 0:
                # TODO: check pre-release incrementing
                return self.from_tuple((self.major, self.minor, self.patch))
            return self.from_tuple((self.major + 1, 0, 0))
        if level == 'minor':
            if self.pre_release and self.patch == 0:
                # TODO: check pre-release incrementing
                return self.from_tuple((self.major, self.minor, self.patch))
            return self.from_tuple((self.major, self.minor + 1, 0))
        if level == 'patch':
            if self.pre_release:
                return self.from_tuple((self.major, self.minor, self.patch))
            return self.from_tuple((self.major, self.minor, self.patch + 1))

        if level == 'premajor':
            return self.from_tuple((self.major + 1, 0, 0, 0))
        if level == 'preminor':
            return self.from_tuple((self.major, self.minor + 1, 0, 0))
        if level == 'prepatch' or (not self.pre_release and level == 'prerelease'):
            return self.from_tuple((self.major, self.minor, self.patch + 1, 0))
        if level == 'prerelease':
            pre = self.pre_release_identifiers
            found_numeric = False
            for i in range(len(pre) - 1, -1, -1):
                if pre[i].isdigit():
                    pre[i] = str(int(pre[i]) + 1)
                    found_numeric = True
                    break
            if not found_numeric:
                pre.append('0')
            return self.from_tuple((self.major, self.minor, self.patch, '.'.join(pre)))

        raise ValueError('Unknown level %s' % level)

    def as_tuple(self):
        return self.major, self.minor, self.patch, self.pre_release, self.build

    def __hash__(self):
        return hash(self.version)

    def __eq__(self, other):
        # NB: strict equality considers pre_release and build versions
        if isinstance(other, str):
            other = self.__class__(other, loose=self.loose)
        elif not isinstance(other, self.__class__):
            raise TypeError('%r is not a version' % other)
        self_short = self.as_tuple()[:3]
        other_short = other.as_tuple()[:3]
        return self_short == other_short and \
            compare_identifiers(self.pre_release_identifiers, other.pre_release_identifiers) and \
            compare_identifiers(self.build_identifiers, other.build_identifiers)

    def __lt__(self, other):
        # NB: strict ordering considers pre_release and build versions
        if isinstance(other, str):
            other = self.__class__(other, loose=self.loose)
        elif not isinstance(other, self.__class__):
            raise TypeError('%r is not a version' % other)
        self_short = self.as_tuple()[:3]
        other_short = other.as_tuple()[:3]
        if self_short < other_short:
            return True

        if self_short == other_short:
            if compare_identifiers(self.pre_release_identifiers, other.pre_release_identifiers, '__lt__'):
                return True
            if compare_identifiers(self.pre_release_identifiers, other.pre_release_identifiers):
                return compare_identifiers(self.build_identifiers, other.build_identifiers, '__lt__')
        return False

        # if self_short == other_short:
        #     if self.pre_release:
        #         if self.pre_release == other.pre_release:
        #             if self.build and other.build:
        #                 return compare_identifiers(self.build_identifiers,
        #                                            other.build_identifiers,
        #                                            '__lt__')
        #             return bool(self.build)
        #         return not other.pre_release or compare_identifiers(self.pre_release_identifiers,
        #                                                             other.pre_release_identifiers,
        #                                                             '__lt__')
        # return False

    def has_same_precedence(self, other):
        # build version is ignored and different pre_release versions are considered equal
        if isinstance(other, str):
            other = self.__class__(other, loose=self.loose)
        elif not isinstance(other, self.__class__):
            raise TypeError('%r is not a version' % other)
        self_short = self.as_tuple()[:3]
        other_short = other.as_tuple()[:3]
        if self_short != other_short:
            return False
        return (not self.pre_release and not other.pre_release) or (self.pre_release and other.pre_release)

    def precedes(self, other):
        # build version is ignored and different pre_release versions are considered equal
        if isinstance(other, str):
            other = self.__class__(other, loose=self.loose)
        elif not isinstance(other, self.__class__):
            raise TypeError('%r is not a version' % other)
        self_short = self.as_tuple()[:3]
        other_short = other.as_tuple()[:3]
        if self_short < other_short:
            return True
        if self_short == other_short:
            return self.pre_release and not other.pre_release
        return False


class Range:
    """
    Implements node-js style of semantic version matching
    https://docs.npmjs.com/misc/semver
    range-set  ::= range ( logical-or range ) *
    logical-or ::= ( ' ' ) * '||' ( ' ' ) *
    range      ::= hyphen | simple ( ' ' simple ) * | ''
    hyphen     ::= partial ' - ' partial
    simple     ::= primitive | partial | tilde | caret
    primitive  ::= ( '<' | '>' | '>=' | '<=' | '=' | ) partial
    partial    ::= xr ( '.' xr ( '.' xr qualifier ? )? )?
    xr         ::= 'x' | 'X' | '*' | nr
    nr         ::= '0' | ['1'-'9'] ( ['0'-'9'] ) *
    tilde      ::= '~' partial
    caret      ::= '^' partial
    qualifier  ::= ( '-' pre )? ( '+' build )?
    pre        ::= parts
    build      ::= parts
    parts      ::= part ( '.' part ) *
    part       ::= nr | [-0-9A-Za-z]+
    """

    def __init__(self, pattern, loose=False):
        self.pattern = pattern
        self.loose = loose
        self.ranges = list(map(self._parse_range, self.pattern.split('||')))

    def _parse_range(self, group):
        identifier = r'[0-9a-z-]+'
        identifiers = r'%s(\.%s)*' % (identifier, identifier)
        version = r'(\d+|x|\*)'
        partial = r'%s+(\.%s(\.%s(\-%s)?(\+%s)?)?)?' % (version, version, version, identifiers, identifiers)

        def hyphen_range(match):
            return '>=%s <=%s' % (match.group('lower'), match.group('higher'))

        # expand hyphen ranges
        group = re.sub(r'(?P<lower>%s)\s+-\s+(?P<higher>%s)' % (partial, partial),
                       hyphen_range,
                       group,
                       flags=re.IGNORECASE)

        def advanced_operator(match):
            if match.group('operator') == '^':
                raise NotImplementedError
            if match.group('operator') == '~':
                raise NotImplementedError
            raise ValueError

        # expand advanced operators
        group = re.sub(r'(?P<operator>[~^])\s*(?P<version>%s)' % partial,
                       advanced_operator,
                       group,
                       flags=re.IGNORECASE)

        # expand incomplete versions
        # make AND comparator set
        print(group)

    def __contains__(self, version):
        if not isinstance(version, Version):
            version = Version(version, loose=self.loose)
        return any(group(version) for group in self.ranges)

    def highest_version(self, versions):
        versions = sorted(filter(lambda version: version in self, map(Version, versions)))
        if versions:
            return versions[-1]
