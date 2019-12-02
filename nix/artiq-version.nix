{ stdenv, git, fetchgit }:
let
    artiq-version = stdenv.mkDerivation {
    name = "artiq-version";
    src = <repoRoot>;
    buildPhase = ''
        REV=`cd modules/artiq && ${git}/bin/git rev-parse HEAD`
        MAJOR_VERSION=`cd modules/artiq && cat MAJOR_VERSION`
        COMMIT_COUNT=`cd modules/artiq && ${git}/bin/git rev-list --count HEAD`
    '';
    installPhase = ''
        echo -n $MAJOR_VERSION.$COMMIT_COUNT.`cut -c1-8 <<< $REV`$SUFFIX > $out
    '';
    };
in
    builtins.readFile artiq-version
