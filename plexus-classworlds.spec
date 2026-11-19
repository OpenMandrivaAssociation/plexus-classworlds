Name:		plexus-classworlds
Version:	2.12.1
Release:	1
Summary:	Plexus Classworlds classloader framework
Group:		Development/Java
License:	Apache-2.0 AND Plexus
URL:		https://github.com/codehaus-plexus/plexus-classworlds
Source0:	%{url}/archive/%{name}-%{version}.tar.gz
Source1:	%{url}/archive/%{name}-2.7.0.tar.gz
BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	javapackages-filesystem
BuildRequires:	sysjar
Requires:	java-current

%description
Classworlds is a framework for container developers who require complex
manipulation of Java's ClassLoaders. This package builds %{version} from
source. 2.12.0 makes loadGlob require every glob segment to match.
2.11 restores the deprecated org.codehaus.classworlds package and sets
Automatic-Module-Name. The 2.7.0 jar is installed beside it for callers
that pin that release.

%prep
%setup -q -n %{name}-%{name}-%{version}
%setup -q -T -D -a 1 -n %{name}-%{name}-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
JAVAC="$JAVA_HOME/bin/javac"

compile_tree() {
	src=$1
	out=$2
	ver=$3
	mkdir -p "$out/classes"
	find "$src/src/main/java" -name '*.java' > "$out/sources.list"
	test -s "$out/sources.list"
	"$JAVAC" --release 8 -proc:none -encoding UTF-8 -d "$out/classes" @"$out/sources.list"
	"$JAVA_HOME/bin/jar" cf "$out/plexus-classworlds.jar" -C "$out/classes" .
	test -s "$out/plexus-classworlds.jar"
	CW_VERSION="$ver" CW_OUT="$out/plexus-classworlds.pom" python - << 'PY'
import os
from pathlib import Path
version = os.environ["CW_VERSION"]
text = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.codehaus.plexus</groupId>
  <artifactId>plexus-classworlds</artifactId>
  <version>CWVER</version>
  <name>Plexus Classworlds</name>
  <description>Classloader framework used by Plexus containers.</description>
  <url>https://github.com/codehaus-plexus/plexus-classworlds</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
      <distribution>repo</distribution>
    </license>
  </licenses>
</project>
"""
Path(os.environ["CW_OUT"]).write_text(text.replace("CWVER", version))
PY
}

compile_tree . cw %{version}
compile_tree plexus-classworlds-plexus-classworlds-2.7.0 cw27 2.7.0
printf 'Manifest-Version: 1.0\nAutomatic-Module-Name: org.codehaus.plexus.classworlds\n' > cw.mf
"$JAVA_HOME/bin/jar" ufm cw/plexus-classworlds.jar cw.mf

%install
sysjar install --buildroot %{buildroot} \
	--artifact "cw27/plexus-classworlds.pom:cw27/plexus-classworlds.jar" \
	--file-name plexus-classworlds-2.7.0 \
	--alias classworlds:classworlds \
	--filelist .mfiles27
/bin/mv %{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-classworlds.sysjar \
	%{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-classworlds-2.7.0.sysjar
sed -i 's|/usr/share/sysjar/index/org.codehaus.plexus/plexus-classworlds\.sysjar|/usr/share/sysjar/index/org.codehaus.plexus/plexus-classworlds-2.7.0.sysjar|' .mfiles27

sysjar install --buildroot %{buildroot} \
	--artifact "cw/plexus-classworlds.pom:cw/plexus-classworlds.jar" \
	--file-name plexus-classworlds \
	--alias classworlds:classworlds \
	--filelist .mfiles
while IFS= read -r line; do
	grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles27

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
cat > CwSmoke.java << 'EOF'
public class CwSmoke {
    public static void main(String[] args) throws Exception {
        org.codehaus.plexus.classworlds.ClassWorld world =
            new org.codehaus.plexus.classworlds.ClassWorld();
        org.codehaus.plexus.classworlds.realm.ClassRealm realm = world.newRealm("pin");
        if (!"pin".equals(realm.getId())) {
            throw new RuntimeException(realm.getId());
        }
        Class<?> loaded = realm.loadClass(String.class.getName());
        if (loaded != String.class) {
            throw new RuntimeException(String.valueOf(loaded));
        }
        System.out.println(args[0] + " " + realm.getId());
    }
}
EOF
"$JAVA_HOME/bin/javac" --release 8 -proc:none -cp cw/plexus-classworlds.jar CwSmoke.java
"$JAVA_HOME/bin/java" -cp "cw/plexus-classworlds.jar:." CwSmoke cw_ok > check.log
cat check.log
grep -F -q 'cw_ok pin' check.log
"$JAVA_HOME/bin/javac" --release 8 -proc:none -cp cw27/plexus-classworlds.jar CwSmoke.java
"$JAVA_HOME/bin/java" -cp "cw27/plexus-classworlds.jar:." CwSmoke cw27_ok > check27.log
cat check27.log
grep -F -q 'cw27_ok pin' check27.log

%files -f .mfiles
%license LICENSE.txt LICENSE-Codehaus.txt
