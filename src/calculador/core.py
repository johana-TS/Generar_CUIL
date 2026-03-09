class CalculadorCUIL:
    """Clase para el cálculo y generación de números CUIL argentinos."""
    
    PREFIJOS = {"M": 20, "F": 27, "I": 23}
    MULTIPLICADORES = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    def calcular(self, dni: int, sexo: str) -> dict:
        """
        Calcula el CUIL a partir del DNI y el sexo.
        
        Args:
            dni (int): Número de DNI.
            sexo (str): Sexo ('M', 'F' o 'I').
            
        Returns:
            dict: {
                "success": bool,
                "data": {"cuil": "20-12345678-9", "prefijo": 20, "dni": "12345678", "digito": 9} | None,
                "error": str | None,
                "codigo": int  (0: éxito, 1: error validación, 2: error cálculo)
            }
        """
        try:
            self._validar_entrada(dni, sexo)
            
            # Normalizar entrada
            dni_str = str(dni).zfill(8)
            sexo = sexo.upper()
            prefijo_inicial = self.PREFIJOS[sexo]
            
            digito, prefijo_final = self._calcular_digito(prefijo_inicial, dni_str)
            
            cuil_str = f"{prefijo_final}-{dni_str}-{digito}"
            
            return {
                "success": True,
                "data": {
                    "cuil": cuil_str,
                    "prefijo": prefijo_final,
                    "dni": dni_str,
                    "digito": digito
                },
                "error": None,
                "codigo": 0
            }
        except ValueError as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "codigo": 1
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"Error interno durante el cálculo: {str(e)}",
                "codigo": 2
            }
            
    def _validar_entrada(self, dni: int, sexo: str) -> None:
        """Valida las entradas antes de procesarlas."""
        if not isinstance(dni, int) or isinstance(dni, bool) or dni <= 0:
            raise ValueError("El DNI debe ser un número entero positivo.")
            
        dni_str = str(dni)
        if len(dni_str) > 8:
            raise ValueError(f"El DNI no puede tener más de 8 dígitos (recibido: {len(dni_str)} dígitos).")
            
        if not isinstance(sexo, str):
            raise ValueError("El sexo debe ser una cadena de texto.")
            
        if sexo.upper() not in self.PREFIJOS:
            raise ValueError(f"El sexo '{sexo}' no es válido. Debe ser uno de: {', '.join(self.PREFIJOS.keys())}.")
            
    def _calcular_digito(self, prefijo: int, dni_str: str) -> tuple:
        """
        Calcula el dígito verificador y maneja el cambio de prefijo en caso de colisión (overflow).
        
        Args:
            prefijo (int): Prefijo inicial según el sexo.
            dni_str (str): DNI formateado a 8 dígitos.
            
        Returns:
            tuple: (digito_verificador, prefijo_final)
        """
        base = f"{prefijo}{dni_str}"
        
        suma = sum(int(digito) * mult for digito, mult in zip(base, self.MULTIPLICADORES))
        resto = suma % 11
        
        if resto == 0:
            digito = 0
            prefijo_final = prefijo
        elif resto == 1:
            if prefijo == 20:
                prefijo_final = 23
                digito = 9
            elif prefijo == 27:
                prefijo_final = 23
                digito = 4
            else:
                # Caso para prefijo 23 u otros
                prefijo_final = 23
                digito = 9
        else:
            digito = 11 - resto
            prefijo_final = prefijo
            
        return digito, prefijo_final
