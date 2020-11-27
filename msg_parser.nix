{ lib, buildPythonPackage, fetchPypi, olefile }:

buildPythonPackage rec {
  pname = "msg_parser";
  version = "1.2.0";

  src = fetchPypi {
    inherit pname version;
    sha256 = "0rmac80knfzlkivr1i37rv6h3zi0gahq7ni8y3vcidpbzka5is0d";
  };

  doCheck = false;
  propagatedBuildInputs = [ olefile ];

  meta = {
    # see https://pypi.org/project/msg-parser
    homepage = https://github.com/vikramarsid/msg_parser;
    description = "Read, parse and convert Microsoft Outlook MSG E-Mail files";
    license = lib.licenses.bsd2;
    maintainers = with lib.maintainers; [ ];
  };
}
