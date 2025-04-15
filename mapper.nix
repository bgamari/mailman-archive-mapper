{ buildPythonApplication, setuptools, dateutil, beautifulsoup4, mailmanPackages }:

buildPythonApplication {
  pname = "mailman-archive-mapper";
  version = "0.1";
  format = "pyproject";
  src = ./.;
  build-system = [ setuptools ];
  propagatedBuildInputs = [
    beautifulsoup4
    mailmanPackages.hyperkitty
    dateutil
  ];
}
