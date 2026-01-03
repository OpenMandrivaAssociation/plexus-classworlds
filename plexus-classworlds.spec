Name:           plexus-classworlds
Version:        2.8.0
Release:        1
Summary:        Plexus Classworlds Classloader Framework
License:        Apache-2.0 AND Plexus
URL:            https://github.com/codehaus-plexus/plexus-classworlds
BuildArch:      noarch

Source0:        %{url}/archive/%{name}-%{version}.tar.gz

BuildRequires:  javapackages-bootstrap

%description
Classworlds is a framework for container developers who require complex
manipulation of Java's ClassLoaders. Java's native ClassLoader mechanisms and
classes can cause much headache and confusion for certain types of application
developers. Projects which involve dynamic loading of components or otherwise
represent a 'container' can benefit from the classloading control provided by
classworlds.

%prep
%autosetup -p1 -C
%mvn_file : %{name} plexus/classworlds
%mvn_alias : classworlds:classworlds

%pom_remove_plugin :maven-dependency-plugin

# These tests depend on artifacts that are not packaged
sed -i /testConfigure_Valid/s/./@org.junit.jupiter.api.Disabled/ src/test/java/org/codehaus/plexus/classworlds/launcher/ConfiguratorTest.java
sed -i /testConfigure_Optionally_Existent/s/./@org.junit.jupiter.api.Disabled/ src/test/java/org/codehaus/plexus/classworlds/launcher/ConfiguratorTest.java

%build
%mvn_build -j

%install
%mvn_install

%files -f .mfiles
%license LICENSE.txt LICENSE-Codehaus.txt
