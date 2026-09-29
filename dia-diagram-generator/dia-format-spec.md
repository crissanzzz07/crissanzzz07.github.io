# Especificación del formato `.dia` para diagramas Entidad-Relación

Documento de referencia para el generador `dia_generator.py`. Describe cómo se
representa en un archivo `.dia` cada elemento de un diagrama E-R/EER
(entidades, atributos, relaciones, participaciones, especialización) y qué reglas
hay que respetar para que **Dia lo abra sin errores y se vea como uno hecho a mano**.

## 0. Cómo leer este documento

**Método.** Todo lo que aquí figura sale de dos fuentes:

1. Tres diagramas hechos a mano en Dia (`AseguradoraHospital_EER`, `Nutrición_EER`,
   `TerapiaFísica_EER_v2_1`): 126 formas ER, 2 triángulos ES y 132 líneas analizadas.
2. Experimentos propios ejecutando **Dia 0.98.0** en modo headless
   (`xvfb-run dia --nosplash -t png -e salida.png entrada.dia`).

Cada afirmación lleva una etiqueta de confianza:

| Etiqueta | Significado |
|---|---|
| **[V]** | Verificado con un experimento contra Dia 0.98. |
| **[O]** | Observado de forma consistente en los archivos originales. |
| **[R]** | Recomendación de diseño del generador (no es una regla del formato). |

Lo que **no** se pudo comprobar se dice expresamente.

Archivos de apoyo en este repositorio: `examples/catalogo_formas.{json,dia,png}`
(catálogo visual de todas las variantes) y `examples/ConflictoBelico_EER.{json,dia,png}`
(diagrama completo de ejemplo).

---

## 1. El contenedor

| Aspecto | Regla |
|---|---|
| Formato | XML 1.0, codificación UTF-8. **[O]** |
| Compresión | Los `.dia` que guarda Dia son **gzip** de ese XML. **[O]** Dia también abre XML **sin comprimir** con extensión `.dia`. **[V]** |
| Declaración `<?xml …?>` | Recomendada; Dia abre el archivo sin ella. **[V]** |
| Namespace | `xmlns:dia="http://www.lysator.liu.se/~alla/dia/"`. Dia **ignora** el valor del namespace (abre igual con uno erróneo), pero se debe escribir el correcto. **[V]** |
| Acentos / ñ | UTF-8 directo (`MÉDICO`, `código`). No hay que escapar nada especial. **[V]** |
| Caracteres XML | Escapar `& < >` como `&amp; &lt; &gt;`. Comillas y `#` dentro de un texto se admiten tal cual. **[V]** |
| Salida de `dia -t dia` | Dia re-guarda el archivo normalizado (recalcula extremos y tamaños). Útil para depurar. **[V]** |

---

## 2. Estructura mínima válida

### 2.1 Esqueleto

```
<dia:diagram xmlns:dia="…">
  <dia:diagramdata> … </dia:diagramdata>      ← opcional; ver §10
  <dia:layer name="Fondo" visible="true" active="true">
    <dia:object type="…" version="…" id="O0"> … </dia:object>
    …
  </dia:layer>
</dia:diagram>
```

* Un `<dia:layer>` es imprescindible: **sin capa Dia abre un diagrama vacío sin avisar**. **[V]**
* Los `id` (`O0`, `O1`, …) deben ser únicos (ver §13).
* Los objetos se referencian entre sí por `id` en `<dia:connections>`.

### 2.2 Ejemplo mínimo completo

Este bloque contiene una entidad, un atributo, una relación, una línea y una
participación, con **solo lo indispensable**. Está verificado: Dia lo abre y lo
exporta sin errores (el script de §15 lo extrae de este documento y lo prueba).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<dia:diagram xmlns:dia="http://www.lysator.liu.se/~alla/dia/">
  <dia:layer name="Fondo" visible="true" active="true">
    <dia:object type="ER - Entity" version="0" id="O0">
      <dia:attribute name="elem_corner"><dia:point val="5,10"/></dia:attribute>
      <dia:attribute name="elem_width"><dia:real val="4.095"/></dia:attribute>
      <dia:attribute name="elem_height"><dia:real val="1.8"/></dia:attribute>
      <dia:attribute name="name"><dia:string>#CLIENTE#</dia:string></dia:attribute>
    </dia:object>
    <dia:object type="ER - Attribute" version="0" id="O1">
      <dia:attribute name="elem_corner"><dia:point val="12,3"/></dia:attribute>
      <dia:attribute name="elem_width"><dia:real val="4.31"/></dia:attribute>
      <dia:attribute name="elem_height"><dia:real val="1.8"/></dia:attribute>
      <dia:attribute name="name"><dia:string>#nombre#</dia:string></dia:attribute>
    </dia:object>
    <dia:object type="ER - Relationship" version="0" id="O2">
      <dia:attribute name="elem_corner"><dia:point val="14,10"/></dia:attribute>
      <dia:attribute name="elem_width"><dia:real val="3.925"/></dia:attribute>
      <dia:attribute name="elem_height"><dia:real val="2.355"/></dia:attribute>
      <dia:attribute name="name"><dia:string>#TIENE#</dia:string></dia:attribute>
      <dia:attribute name="left_card"><dia:string>#1#</dia:string></dia:attribute>
      <dia:attribute name="right_card"><dia:string>#N#</dia:string></dia:attribute>
    </dia:object>
    <dia:object type="Standard - Line" version="0" id="O3">
      <dia:attribute name="conn_endpoints">
        <dia:point val="13,4.8"/>
        <dia:point val="8,10"/>
      </dia:attribute>
      <dia:connections>
        <dia:connection handle="0" to="O1" connection="8"/>
        <dia:connection handle="1" to="O0" connection="8"/>
      </dia:connections>
    </dia:object>
    <dia:object type="ER - Participation" version="1" id="O4">
      <dia:attribute name="orth_points">
        <dia:point val="9.095,10.9"/>
        <dia:point val="11.5475,10.9"/>
        <dia:point val="11.5475,11.1775"/>
        <dia:point val="14,11.1775"/>
      </dia:attribute>
      <dia:attribute name="orth_orient">
        <dia:enum val="0"/><dia:enum val="1"/><dia:enum val="0"/>
      </dia:attribute>
      <dia:attribute name="autorouting"><dia:boolean val="true"/></dia:attribute>
      <dia:connections>
        <dia:connection handle="0" to="O0" connection="4"/>
        <dia:connection handle="1" to="O2" connection="0"/>
      </dia:connections>
    </dia:object>
  </dia:layer>
</dia:diagram>
```

### 2.3 Qué es obligatorio y qué no

| Objeto | **Obligatorio** (si falta, Dia se cierra o el elemento no funciona) | Opcional (Dia usa su valor por defecto) |
|---|---|---|
| `ER - Entity` | `name` **[V]** — sin él **Dia se cierra con segfault** al dibujar | `elem_width`/`elem_height` (Dia reajusta el tamaño al texto; `elem_corner` conviene darlo siempre, no se probó sin él), `obj_pos`, `obj_bb`, `border_*`, `inner_color`, `weak`, `associative`, `font`, `font_height` |
| `ER - Attribute` | `name` **[V]** — sin él, segfault | igual que arriba + `key`, `weak_key`, `derived`, `multivalued` (por defecto `false`) |
| `ER - Relationship` | `name`, `left_card` y `right_card` **[V]** — si falta cualquiera, **segfault**. Las cardinalidades pueden ir vacías (`<dia:string>##</dia:string>`), pero **deben existir** | resto de propiedades (`identifying`, `rotated` por defecto `false`) |
| `Standard - Line` | `conn_endpoints` + `<dia:connections>` | `obj_pos`, `obj_bb`, `numcp` **[V]** |
| `ER - Participation` | `orth_points`, `orth_orient` (n−1 valores), `<dia:connections>` | `autorouting`, `total` (valor por defecto no verificado: escribirlos siempre) |
| `Flowchart - Merge` | geometría (`elem_corner/width/height`) **[V]** abre; para que se vea el "ES" hay que dar el bloque `text` completo | resto |

> **[R]** El generador escribe siempre la **forma completa** (todas las propiedades
> que Dia serializa), no la mínima: es más predecible, se ve igual que un archivo
> hecho a mano y no depende de valores por defecto que no están verificados.

---

## 3. Tipos de datos XML

Todos son hijos de `<dia:attribute name="…">`:

| Elemento | Ejemplo | Uso |
|---|---|---|
| `<dia:point val="x,y"/>` | `val="16.65,7.9"` | Coordenadas (cm). Varios `point` seguidos forman una lista. |
| `<dia:rectangle val="x0,y0;x1,y1"/>` | `val="16.6,7.85;21.18,9.75"` | Caja envolvente (`obj_bb`). |
| `<dia:real val="…"/>` | `val="0.8"` | Números decimales (punto decimal). |
| `<dia:int val="…"/>` | `val="1"` | Enteros (`numcp`). |
| `<dia:boolean val="true\|false"/>` | | Banderas. |
| `<dia:string>#texto#</dia:string>` | `#CLIENTE#` | **Los textos van entre almohadillas.** Sin ellas Dia da `Error in file, string not starting with #` y pierde el texto. **[V]** |
| `<dia:color val="#rrggbb"/>` | `#000000` | Dia guarda `#rrggbbaa`; ambas formas se aceptan. **[V]** |
| `<dia:font family style name/>` | `family="monospace" style="0" name="Courier"` | Fuente. |
| `<dia:enum val="n"/>` | `val="1"` | Enumeraciones (orientación, alineación). |
| `<dia:composite type="…">` | | Agrupa atributos (texto, papel, rejilla). |

---

## 4. Sistema de coordenadas y unidades

* Unidad: **centímetros**. **[O]**
* Origen arriba a la izquierda, **`x` crece hacia la derecha e `y` hacia abajo**. **[O]**
* Una forma se posiciona por su **esquina superior izquierda** (`elem_corner`, igual
  que `obj_pos`) más `elem_width` y `elem_height`. **[O]**
* Si se conoce el **centro** (cx, cy): `corner = (cx − w/2, cy − h/2)`. **[R]**
* Las coordenadas de los diagramas hechos a mano son decimales arbitrarios
  (`5.94235`), porque nacen de arrastrar con el ratón. **[O]** El generador debe
  producir posiciones **alineadas** (ver §14).
* Rejilla de Dia por defecto: 1 cm × 1 cm. **[O]**

---

## 5. Objetos ER

En los fragmentos siguientes se abrevia cada `<dia:attribute>` a una línea; Dia los
escribe en varias y la indentación no importa.

### 5.1 Entidad — `ER - Entity` (versión `0`)

```xml
<dia:object type="ER - Entity" version="0" id="O0">
  <dia:attribute name="obj_pos"><dia:point val="16.65,7.9"/></dia:attribute>
  <dia:attribute name="obj_bb"><dia:rectangle val="16.6,7.85;21.18,9.75"/></dia:attribute>
  <dia:attribute name="elem_corner"><dia:point val="16.65,7.9"/></dia:attribute>
  <dia:attribute name="elem_width"><dia:real val="4.48"/></dia:attribute>
  <dia:attribute name="elem_height"><dia:real val="1.8"/></dia:attribute>
  <dia:attribute name="border_width"><dia:real val="0.1"/></dia:attribute>
  <dia:attribute name="border_color"><dia:color val="#000000"/></dia:attribute>
  <dia:attribute name="inner_color"><dia:color val="#ffffff"/></dia:attribute>
  <dia:attribute name="name"><dia:string>#HOSPITAL#</dia:string></dia:attribute>
  <dia:attribute name="weak"><dia:boolean val="false"/></dia:attribute>
  <dia:attribute name="associative"><dia:boolean val="false"/></dia:attribute>
  <dia:attribute name="font"><dia:font family="monospace" style="0" name="Courier"/></dia:attribute>
  <dia:attribute name="font_height"><dia:real val="0.8"/></dia:attribute>
</dia:object>
```

| Propiedad | Efecto visual **[V]** |
|---|---|
| `weak = true` | **Entidad débil**: doble borde. |
| `associative = true` | **Entidad asociativa**: rombo dibujado dentro del rectángulo. *(Ninguno de los archivos originales la usa; comprobado solo en el catálogo.)* |

### 5.2 Atributo — `ER - Attribute` (versión `0`)

Misma estructura que la entidad, con estas propiedades propias en lugar de
`weak`/`associative`:

```xml
<dia:attribute name="name"><dia:string>#código_hospital#</dia:string></dia:attribute>
<dia:attribute name="key"><dia:boolean val="true"/></dia:attribute>
<dia:attribute name="weak_key"><dia:boolean val="false"/></dia:attribute>
<dia:attribute name="derived"><dia:boolean val="false"/></dia:attribute>
<dia:attribute name="multivalued"><dia:boolean val="false"/></dia:attribute>
```

| Propiedad | Notación EER | Efecto visual **[V]** |
|---|---|---|
| ninguna | Atributo simple | Óvalo. |
| `key` | Clave primaria | Texto **subrayado** continuo. |
| `weak_key` | Clave parcial (discriminante) | Texto subrayado **punteado**. |
| `derived` | Atributo derivado | Óvalo con **borde punteado**. |
| `multivalued` | Multivalor | **Doble óvalo**. |

Las banderas pueden combinarse (p. ej. `key` + `weak_key` aparece en `Nutrición_EER`). **[O]**

### 5.3 Relación — `ER - Relationship` (versión `0`)

```xml
<dia:object type="ER - Relationship" version="0" id="O21">
  <!-- obj_pos, obj_bb, elem_corner, elem_width, elem_height, border_*, inner_color como en §5.1 -->
  <dia:attribute name="name"><dia:string>#CUBRE#</dia:string></dia:attribute>
  <dia:attribute name="left_card"><dia:string>#1#</dia:string></dia:attribute>
  <dia:attribute name="right_card"><dia:string>#N#</dia:string></dia:attribute>
  <dia:attribute name="identifying"><dia:boolean val="true"/></dia:attribute>
  <dia:attribute name="rotated"><dia:boolean val="true"/></dia:attribute>
  <!-- font, font_height como en §5.1 -->
</dia:object>
```

| Propiedad | Efecto visual **[V]** |
|---|---|
| `identifying = true` | **Relación identificadora**: doble rombo (la que une una entidad débil con su propietaria). |
| `rotated = false` | Etiquetas de cardinalidad en los vértices **izquierdo** (`left_card`) y **derecho** (`right_card`). |
| `rotated = true` | Etiquetas en los vértices **superior** (`left_card`) e **inferior** (`right_card`). Se usa para relaciones que unen entidades en vertical. |
| `left_card`, `right_card` | Texto libre (`1`, `N`, `M`, `≤3`, `0..1`…). Admiten Unicode. |

**Advertencia — caja de exportación con `rotated`.** Con `rotated = true` Dia 0.98
calcula un `obj_bb` cuyo borde derecho crece proporcionalmente a la coordenada X
del rombo (X≈95 → ancho ≈100 cm de más). No afecta al dibujo, pero **ensancha el
lienzo al exportar a PNG/SVG**. **[V]** Ocurre también en los archivos originales
(`CUBRE`), y no se arregla dando un `obj_bb` correcto. Solución del proyecto: recortar
el margen blanco de las vistas previas (`render_preview.py`). Se conserva `rotated`
porque es lo que usa un diagrama hecho a mano.

### 5.4 Línea atributo↔forma — `Standard - Line` (versión `0`)

```xml
<dia:object type="Standard - Line" version="0" id="O3">
  <dia:attribute name="obj_pos"><dia:point val="18.8638,9.7478"/></dia:attribute>
  <dia:attribute name="obj_bb"><dia:rectangle val="18.7889,9.69644;18.9152,10.6512"/></dia:attribute>
  <dia:attribute name="conn_endpoints">
    <dia:point val="18.8638,9.7478"/>
    <dia:point val="18.8403,10.5998"/>
  </dia:attribute>
  <dia:attribute name="numcp"><dia:int val="1"/></dia:attribute>
  <dia:connections>
    <dia:connection handle="0" to="O0" connection="8"/>
    <dia:connection handle="1" to="O75" connection="12"/>
  </dia:connections>
</dia:object>
```

* Une un **atributo con su entidad o relación**, y una **entidad con el triángulo ES**.
* `handle="0"` es el extremo inicial y `handle="1"` el final; el orden es indiferente.
* **Regla clave [V]:** si se conecta por el punto **`8`** (centro con *autogap*) Dia
  **recoloca el extremo en el borde de la forma** al cargar, aunque las
  coordenadas escritas sean erróneas (se probó con `0,0 → 50,50`). Con los puntos
  `0–7` **no** se recoloca: el extremo queda donde se escriba. Por eso las líneas de
  atributo se conectan siempre por `8`.
* `numcp` (1 en todos los originales) no es necesario. **[V]**

### 5.5 Participación entidad↔relación — `ER - Participation` (versión `1`)

Línea **ortogonal** (segmentos horizontales y verticales) que une una entidad con una relación.

```xml
<dia:object type="ER - Participation" version="1" id="O23">
  <dia:attribute name="obj_pos"><dia:point val="36.505,11.5579"/></dia:attribute>
  <dia:attribute name="obj_bb"><dia:rectangle val="36.455,11.5079;36.5625,13.451"/></dia:attribute>
  <dia:attribute name="orth_points">
    <dia:point val="36.505,11.5579"/> <dia:point val="36.505,12.4795"/>
    <dia:point val="36.5125,12.4795"/> <dia:point val="36.5125,13.401"/>
  </dia:attribute>
  <dia:attribute name="orth_orient">
    <dia:enum val="1"/><dia:enum val="0"/><dia:enum val="1"/>
  </dia:attribute>
  <dia:attribute name="autorouting"><dia:boolean val="true"/></dia:attribute>
  <dia:attribute name="total"><dia:boolean val="false"/></dia:attribute>
  <dia:connections>
    <dia:connection handle="0" to="O16" connection="8"/>
    <dia:connection handle="1" to="O21" connection="8"/>
  </dia:connections>
</dia:object>
```

| Propiedad | Regla |
|---|---|
| `orth_points` | Lista de puntos del trazado; **4 puntos** en todos los originales. **[O]** |
| `orth_orient` | Un `enum` por segmento (**n−1** valores): `0` = horizontal, `1` = vertical. Un trazado horizontal–vertical–horizontal es `0,1,0`; vertical–horizontal–vertical es `1,0,1`. **[O]** |
| `autorouting = true` | **Dia recalcula la ruta al cargar** a partir de los puntos de conexión reales; los `orth_points` escritos solo sirven de aproximación (se probó con puntos basura: salió un trazado limpio). Con `false` respeta los puntos, aunque estén mal. **[V]** → **escribir siempre `true`**. |
| `total = true` | **Participación total**: dibuja la línea **doble**. |
| `connection` | Índices `0–7` para elegir el lado exacto (§8) o `8` para dejar que Dia elija. |

### 5.6 Especialización (triángulo ES) — `Flowchart - Merge` (versión `1`)

No es un objeto ER sino un símbolo de diagrama de flujo; es el que usan los diagramas
originales para la relación *"es un"*.

```xml
<dia:object type="Flowchart - Merge" version="1" id="O75">
  <dia:attribute name="obj_pos"><dia:point val="17.696,10.65"/></dia:attribute>
  <dia:attribute name="obj_bb"><dia:rectangle val="17.6147,10.6;20.0023,12.9608"/></dia:attribute>
  <dia:attribute name="meta"><dia:composite type="dict"/></dia:attribute>
  <dia:attribute name="elem_corner"><dia:point val="17.696,10.65"/></dia:attribute>
  <dia:attribute name="elem_width"><dia:real val="2.225"/></dia:attribute>
  <dia:attribute name="elem_height"><dia:real val="2.2"/></dia:attribute>
  <dia:attribute name="line_width"><dia:real val="0.1"/></dia:attribute>
  <dia:attribute name="line_colour"><dia:color val="#000000"/></dia:attribute>
  <dia:attribute name="fill_colour"><dia:color val="#ffffff"/></dia:attribute>
  <dia:attribute name="show_background"><dia:boolean val="true"/></dia:attribute>
  <dia:attribute name="line_style"><dia:enum val="0"/><dia:real val="1"/></dia:attribute>
  <dia:attribute name="padding"><dia:real val="0.1"/></dia:attribute>
  <dia:attribute name="text">
    <dia:composite type="text">
      <dia:attribute name="string"><dia:string>#ES#</dia:string></dia:attribute>
      <dia:attribute name="font"><dia:font family="sans" style="0" name="Helvetica"/></dia:attribute>
      <dia:attribute name="height"><dia:real val="0.8"/></dia:attribute>
      <dia:attribute name="pos"><dia:point val="18.8085,11.4"/></dia:attribute>
      <dia:attribute name="color"><dia:color val="#000000"/></dia:attribute>
      <dia:attribute name="alignment"><dia:enum val="1"/></dia:attribute>
    </dia:composite>
  </dia:attribute>
  <dia:attribute name="flip_horizontal"><dia:boolean val="false"/></dia:attribute>
  <dia:attribute name="flip_vertical"><dia:boolean val="false"/></dia:attribute>
  <dia:attribute name="subscale"><dia:real val="1"/></dia:attribute>
</dia:object>
```

* Tamaño fijo: **2.225 × 2.2**. **[O]**
* `flip_vertical = false` → triángulo **▽** (base arriba): padre encima, hijos debajo,
  como en los originales. `flip_vertical = true` → **△**: padre debajo e hijos encima. **[V]**
* Texto: fuente `sans/Helvetica` (no la Courier de las formas ER), `alignment 1` = centrado.
  `pos` = (centro X, esquina superior Y + 0.75) en ▽. **[O]**
* Las líneas (`Standard - Line`) del padre y de cada hijo se conectan al triángulo
  por el punto **`12`** y a la entidad por `8`; ambos extremos se recolocan solos. **[O]**
  El diagrama de ejemplo usa un único triángulo con 1 padre y 4 hijos. **[V]**
* El símbolo **no distingue** especialización disjunta/solapada ni total/parcial.

### 5.7 Texto suelto — `Standard - Text` (versión `1`)

Sirve para lo que las formas ER no traen, por ejemplo la **tercera cardinalidad** de
una relación ternaria (el rombo solo tiene dos etiquetas). Tal como lo re-serializa Dia: **[V]**

```xml
<dia:object type="Standard - Text" version="1" id="O24">
  <dia:attribute name="obj_pos"><dia:point val="95.4,42.655"/></dia:attribute>
  <dia:attribute name="obj_bb"><dia:rectangle val="95.4,42.06;95.785,42.8075"/></dia:attribute>
  <dia:attribute name="text">
    <dia:composite type="text">
      <dia:attribute name="string"><dia:string>#P#</dia:string></dia:attribute>
      <dia:attribute name="font"><dia:font family="monospace" style="0" name="Courier"/></dia:attribute>
      <dia:attribute name="height"><dia:real val="0.8"/></dia:attribute>
      <dia:attribute name="pos"><dia:point val="95.4,42.655"/></dia:attribute>
      <dia:attribute name="color"><dia:color val="#000099"/></dia:attribute>
      <dia:attribute name="alignment"><dia:enum val="0"/></dia:attribute>
    </dia:composite>
  </dia:attribute>
  <dia:attribute name="valign"><dia:enum val="3"/></dia:attribute>
</dia:object>
```

`pos` es el origen del texto (línea base, alineado a la izquierda con `alignment 0`).
Color `#000099` para imitar el azul de las etiquetas de cardinalidad de Dia.
*No se ha probado en un archivo mínimo:* usar siempre esta forma completa.

---

## 6. Tamaños estándar y fórmulas

**Todas las formas ER usan `monospace/Courier`, altura 0.8**, así que el ancho es
proporcional al número de caracteres `n` del nombre (los acentos cuentan como 1).
Las fórmulas se ajustaron con los 126 objetos de los tres archivos y **cuadran sin
ningún residuo**. **[O]** También coinciden con lo que Dia calcula al cargar. **[V]**

| Forma | Ancho `w` | Alto `h` |
|---|---|---|
| `ER - Entity` | `0.385·n + 1.4` | `1.8` |
| `ER - Attribute` | `0.385·n + 2.0` | `1.8` |
| `ER - Relationship` | `0.385·n + 2.0` | `0.6·w` |
| `Flowchart - Merge` (ES) | `2.225` | `2.2` |

Ejemplos: `HOSPITAL` (8) → 4.48 × 1.8; `código_hospital` (15) → atributo 7.775 × 1.8;
`CUBRE` (5) → relación 3.925 × 2.355.

**Qué pasa si el tamaño escrito no cumple la fórmula [V]:** Dia **lo corrige al
cargar**, haciendo crecer la forma desde su esquina hacia la derecha y abajo (se probó
con ancho 2.0 para un texto largo). El archivo se abre bien, pero **la forma ocupa
más de lo previsto y puede solaparse con las vecinas**. Por eso el generador debe
calcular los tamaños con estas fórmulas *antes* de situar nada.

Constantes de estilo comunes: `border_width 0.1`, `border_color #000000`,
`inner_color #ffffff`, `font_height 0.8`. **[O]**

---

## 7. Propiedades de texto y estilos

| Elemento | Fuente | Altura | Color |
|---|---|---|---|
| Nombre en entidad, atributo, relación | `monospace` / `Courier`, `style="0"` | `0.8` | Por defecto de Dia |
| Texto del triángulo ES | `sans` / `Helvetica`, `style="0"` | `0.8` (`alignment 1`) | `#000000` |
| Etiquetas de cardinalidad | Las dibuja la relación con su fuente | — | Azul oscuro de Dia |
| Texto suelto | `monospace` / `Courier` | `0.8` | `#000099` (elección propia) |

Todas las líneas y bordes: negro `#000000`, grosor `0.1`. Relleno blanco `#ffffff`.
El estilo por defecto de Dia ya es el de los diagramas originales, por lo que no
hace falta nada más para "verse profesional".

---

## 8. Conexión de objetos

### 8.1 La regla básica

Una conexión se declara en `<dia:connections>` de la **línea**:

```xml
<dia:connection handle="0" to="O16" connection="8"/>
```

* `handle`: extremo de la línea (`0` inicial, `1` final).
* `to`: `id` del objeto destino. **Debe existir**, o Dia da `Linked object not found in document`. **[V]**
* `connection`: **índice del punto de conexión** del destino. Si el índice no existe
  en ese tipo de objeto, Dia da `Connection point N does not exist on 'ER - Entity'`. **[V]**

### 8.2 Puntos de conexión por tipo de objeto **[V]**

Se midieron cargando un archivo con líneas autorruteadas a cada índice y leyendo la
posición donde Dia las ancló.

**`ER - Entity`** y rectángulos (posición relativa a la caja; `w`, `h` = tamaño):

| Índice | Punto | | Índice | Punto |
|:-:|---|---|:-:|---|
| `0` | esquina sup. izq. | | `4` | centro derecha |
| `1` | centro arriba | | `5` | esquina inf. izq. |
| `2` | esquina sup. der. | | `6` | centro abajo |
| `3` | centro izquierda | | `7` | esquina inf. der. |
| **`8`** | **centro, con *autogap* (Dia recorta la línea en el borde)** | | | |

**`ER - Relationship`** (rombo):

| Índice | Punto | | Índice | Punto |
|:-:|---|---|:-:|---|
| `0` | vértice izquierdo | | `4` | vértice derecho |
| `1` | punto medio de la arista NO | | `5` | punto medio de la arista SO |
| `2` | vértice superior | | `6` | vértice inferior |
| `3` | punto medio de la arista NE | | `7` | punto medio de la arista SE |
| **`8`** | **centro con *autogap*** | | | |

**`ER - Attribute`** (óvalo): usar **solo `8`** (es lo único que emplean los originales). **[O]**

**`Flowchart - Merge`** (triángulo ▽ sin voltear):

| Índice | Punto |
|:-:|---|
| `0, 1, 2, 3, 4` | borde superior, en x/w = 0, ¼, ½, ¾, 1 |
| `8` | vértice inferior |
| **`12`** | **centro con *autogap*** (el que usan los originales) |
| `5–7`, `9–11` | no se posicionan de forma fiable: **no usar** |

### 8.3 Cuándo usar `8` y cuándo un punto fijo

| Situación | Conexión | Por qué |
|---|---|---|
| Atributo ↔ entidad / relación | `8` en ambos extremos | Dia coloca el extremo en el borde solo. |
| Entidad ↔ triángulo ES | `8` (entidad) y `12` (triángulo) | Ídem. |
| Entidad ↔ relación (participación) | `0–7` para forzar el lado, o `8` | La línea ortogonal se re-enruta sola (`autorouting`), así que se elige el lado que dé el trazado más limpio. |

### 8.4 Patrones de conexión

Todos verificados en `examples/ConflictoBelico_EER.dia`. **[V]**

| Patrón | Cómo se dibuja |
|---|---|
| **Binaria** en horizontal | Entidad `4` (der.) → rombo `0` (izq.); rombo `4` → entidad `3`. Trazado recto si están a la misma altura. |
| **Binaria** en vertical | Entidad `6` (abajo) → rombo `2` (arriba); rombo `6` → entidad `1`. El rombo con `rotated = true`. |
| **Desalineada** (en L) | Rombo `0/4` (sale en horizontal) → entidad `1/6` (entra en vertical), o al revés. Dia hace el codo. |
| **Recursiva** | Dos participaciones a la **misma entidad**: rombo `0` → entidad `5` (inf. izq.) y rombo `4` → entidad `7` (inf. der.), con el rombo debajo. Queda en forma de "copa", igual que el `JEFE_DE` de los originales. |
| **Ternaria** | Tres participaciones a un mismo rombo por lados distintos: `0` (izq.), `4` (der.) y `6` (abajo). Solo hay 2 etiquetas de cardinalidad: la tercera va como `Standard - Text` (§5.7). |
| **Atributo de relación** | `Standard - Line` de un óvalo al rombo, por `8` en ambos extremos. |
| **Especialización** | 1 línea padre→ES y 1 línea ES→cada hijo (`8`/`12`). |

---

## 9. Cardinalidades y participación

* `left_card` y `right_card` son **texto libre** en la relación; no están ligados a
  ninguna entidad concreta: **su posición decide a quién corresponden**.
* Con `rotated = false`, `left_card` se dibuja junto al vértice **izquierdo** del rombo y
  `right_card` junto al **derecho**. Con `rotated = true`, `left_card` va arriba y
  `right_card` abajo. **[V]** Por tanto, la entidad situada a la izquierda (o arriba) debe
  recibir el valor de `left_card`.
* El generador coloca junto a cada entidad el texto de cardinalidad que se le indique
  para ella (p. ej. una relación M:N lleva `M` junto a una entidad y `N` junto a la otra);
  qué convención de lectura se siga (aquí o allá) es decisión del autor del diagrama.
* Participación **total** = `total="true"` en esa `Participation` (línea doble).
  Participación **parcial** = línea simple.
* Las cotas del tipo "como máximo 3" no tienen símbolo propio: se escriben en el texto
  de la etiqueta (`≤3`, `0..1`). **[V]** (`≤` se dibuja correctamente).

---

## 10. Cabecera `<dia:diagramdata>`

Es **opcional**: Dia abre el archivo sin ella (y con solo `background`). **[V]**
Los originales llevan la cabecera completa, que conviene reproducir:

```xml
<dia:diagramdata>
  <dia:attribute name="background"><dia:color val="#ffffff"/></dia:attribute>
  <dia:attribute name="pagebreak"><dia:color val="#000099"/></dia:attribute>
  <dia:attribute name="paper">
    <dia:composite type="paper">
      <dia:attribute name="name"><dia:string>#A4#</dia:string></dia:attribute>
      <dia:attribute name="tmargin"><dia:real val="2.54"/></dia:attribute>
      <dia:attribute name="bmargin"><dia:real val="2.54"/></dia:attribute>
      <dia:attribute name="lmargin"><dia:real val="2.54"/></dia:attribute>
      <dia:attribute name="rmargin"><dia:real val="2.54"/></dia:attribute>
      <dia:attribute name="is_portrait"><dia:boolean val="false"/></dia:attribute>
      <dia:attribute name="scaling"><dia:real val="1"/></dia:attribute>
      <dia:attribute name="fitto"><dia:boolean val="false"/></dia:attribute>
    </dia:composite>
  </dia:attribute>
  <dia:attribute name="grid">
    <dia:composite type="grid">
      <dia:attribute name="width_x"><dia:real val="1"/></dia:attribute>
      <dia:attribute name="width_y"><dia:real val="1"/></dia:attribute>
      <dia:attribute name="visible_x"><dia:int val="1"/></dia:attribute>
      <dia:attribute name="visible_y"><dia:int val="1"/></dia:attribute>
      <dia:composite type="color"/>
    </dia:composite>
  </dia:attribute>
  <dia:attribute name="color"><dia:color val="#d8e5e5"/></dia:attribute>
  <dia:attribute name="guides">
    <dia:composite type="guides">
      <dia:attribute name="hguides"/>
      <dia:attribute name="vguides"/>
    </dia:composite>
  </dia:attribute>
</dia:diagramdata>
```

* Papel: los originales usan `Legal` y `Letter`; el generador usa `A4`/`A3` sin
  problemas. **[V]** Otros nombres siguen la lista de papeles de Dia (no verificados uno a uno).
* La capa se llama `Fondo` en los originales (Dia en español); el nombre es libre.

---

## 11. Identificadores y orden de dibujado

* Los `id` son `O0`, `O1`, … en orden de creación. **[O]** Basta con que sean cadenas únicas.
* El **orden de aparición en el archivo es el orden de dibujado** (lo posterior queda
  encima). **[O]** En los originales las líneas se intercalan con las formas. **[R]** El
  generador escribe primero todas las formas y después todas las líneas.
* **Ids duplicados: Dia los acepta en silencio** y dibuja ambos objetos, pero las
  conexiones a ese `id` quedan ambiguas. **[V]** Hay que impedirlos en el generador.

---

## 12. Comportamientos de Dia que condicionan el generador

| # | Comportamiento | Consecuencia |
|---|---|---|
| 1 | Al cargar, Dia **recoloca los extremos** de líneas conectadas por `8` y **re-enruta** las participaciones con `autorouting`. **[V]** | Las coordenadas de líneas no tienen que ser exactas, **las conexiones sí**. |
| 2 | Dia **corrige el tamaño** de las formas al del texto (§6). **[V]** | Usar las fórmulas de tamaño. |
| 3 | Los extremos en puntos fijos `0–7` de una `Standard - Line` **no** se recolocan. **[V]** | Para líneas simples, conectar por `8`. |
| 4 | Un rombo `rotated` **ensancha la caja de exportación**. **[V]** | Recortar las vistas previas. |
| 5 | Dia recalcula `obj_bb`. **[V]** | Su valor en el archivo no es crítico. |
| 6 | Dia **se cierra** si faltan `name` (entidad/atributo/relación) o `left_card`/`right_card` (relación). **[V]** | Escribirlos siempre. |
| 7 | `dia -t png` devuelve **código 0 con errores de contenido** (conexiones rotas, textos mal formados…); solo devuelve `1` con XML mal formado y `139` con segfault. **[V]** | La prueba debe **leer stderr** (§13), no fiarse del código. |
| 8 | Con `segfault` (código 139) puede quedar un PNG **inválido** en disco. **[V]** | Comprobar que la imagen se abre. |

---

## 13. Errores conocidos y validación

Resultado de cada tipo de fallo, probado contra Dia 0.98. La columna
*"Qué dibuja"* indica si se pierde contenido **en silencio**.

| Fallo | Código de salida | Mensaje de Dia | Qué dibuja |
|---|:-:|---|---|
| XML mal formado (etiqueta sin cerrar) | `1` | `parser error : Opening and ending tag mismatch` | Nada. |
| `connection` a un `id` inexistente | `0` | `Error loading diagram. Linked object not found in document.` | Parcial. |
| Índice de punto de conexión inexistente | `0` | `Connection point 42 does not exist on 'ER - Entity'.` | Parcial. |
| `<dia:string>` sin `#…#` | `0` | `Error in file, string not starting with #` | Forma sin texto. |
| Tipo de objeto desconocido | `0` | `WARNING: Unable to find object type: ER - Foo` | Omite ese objeto. |
| Falta `name` / `left_card` / `right_card` | `139` | (ninguno: segfault) | PNG inválido. |
| Sin `<dia:layer>` | `0` | (ninguno) | **Diagrama vacío en silencio.** |
| `id` duplicado | `0` | (ninguno) | Dibuja ambos; conexiones ambiguas. |
| Namespace incorrecto | `0` | (ninguno) | Lo abre igual. |

### Lista de comprobaciones del validador (Pasos 3 y 4)

El generador y la prueba deben, **antes de dar por bueno un archivo**:

1. Parsear el XML con un parser estricto (`xml.etree`), y confirmar el namespace correcto.
2. Existencia de **una capa** y de al menos un objeto.
3. **`id` únicos**.
4. Cada `<dia:connection>` apunta a un `id` existente y su `connection` es válido para
   el tipo destino (`0–8` en entidad/rombo/atributo; `0–4, 8, 12` en ES).
5. Cada línea/participación tiene **ambos extremos conectados** (evita las líneas
   flotantes que sí tenía un archivo original).
6. Entidad/atributo/relación con `name`; relación con `left_card` y `right_card`.
7. Cada `dia:string` de texto va entre `#…#`.
8. `orth_orient` tiene `len(orth_points) − 1` valores.
9. Cargar con Dia real y exportar: **stderr sin `Error`/`CRITICAL`/`WARNING`, código de
   salida 0 y PNG legible** (recortado; ver §12).

---

## 14. Recomendaciones de layout (para alineación profesional)

*Todo lo de esta sección es [R]: nace de dibujar el diagrama de "Conflicto Bélico"
con 13 entidades, 36 atributos y 11 relaciones, no es una regla del formato.*

1. **Posicionar por centros y alinear en filas/columnas.** Entidades y rombos de una
   misma fila comparten `cy`; los de una columna comparten `cx`. Así las participaciones
   salen rectas. Redondear centros a múltiplos de **0.5 cm**.
2. **Retícula de entidades:** una entidad con varias relaciones se rodea de sus rombos
   en los 4 lados (izq./der./arriba/abajo). Dejar entre el borde de la entidad y el vértice
   del rombo ≥ **4 cm** para que quepan la línea y la etiqueta de cardinalidad.
3. **Atributos en las diagonales libres.** Situar los óvalos **en diagonal** respecto a
   su entidad, nunca sobre los ejes por donde salen las participaciones; así la línea del
   atributo no se solapa con otra. Separar los óvalos entre sí ≥ 1.5 cm.
4. **Ninguna línea atraviesa una forma.** Un atributo colocado en el recorrido de una
   participación queda "tachado" (pasó con `total_armas`). Revisar cada óvalo contra las
   líneas ortogonales.
5. **Atributos de relación:** por encima o por debajo del rombo, en el espacio libre
   entre columnas.
6. **Especialización:** padre y triángulo en la misma `x`; hijos repartidos de forma
   simétrica y a la misma `y`; sus atributos alineados encima/debajo de cada hijo.
   Usar `voltear` cuando los hijos van **encima** del padre.
7. **Relación vertical:** usar `rotated = true` para que las cardinalidades queden
   arriba/abajo (cuesta el ensanchado de la caja de exportación, §5.3).
8. **Relación recursiva:** rombo debajo de la entidad (o encima), lados `5`/`7` de la
   entidad (o `0`/`2`). Es el estilo "copa" de los diagramas de origen.
9. **Solapes:** con las fórmulas de §6 se puede calcular la caja de cada forma y
   detectar solapes antes de escribir el archivo.

---

## 15. Verificación reproducible

Requiere `dia`, `xvfb-run` y Pillow.

```bash
# Abrir y exportar (el aviso "--size parameter unsupported" y el SyntaxWarning son inofensivos)
xvfb-run -a dia --nosplash -t png -e salida.png entrada.dia

# Vista previa recortada
python3 render_preview.py entrada.dia salida.png

# Ver cómo re-serializa Dia un archivo (recalcula extremos y tamaños)
xvfb-run -a dia --nosplash -t dia -e normalizado.dia entrada.dia

# Verificar el ejemplo mínimo de §2.2 (lo extrae de este documento)
python3 - <<'PY'
import re, subprocess, os, tempfile
md = open("dia-format-spec.md", encoding="utf-8").read()
xml = re.search(r"### 2\.2.*?```xml\n(.*?)```", md, re.S).group(1)
d = tempfile.mkdtemp(); src, out = d + "/min.dia", d + "/min.png"
open(src, "w", encoding="utf-8").write(xml)
r = subprocess.run(["xvfb-run", "-a", "dia", "--nosplash", "-t", "png", "-e", out, src],
                   capture_output=True, text=True)
bad = [l for l in (r.stderr + r.stdout).splitlines()
       if any(k in l for k in ("Error", "CRITICAL", "WARNING")) and "size parameter" not in l]
print("código", r.returncode, "| PNG", os.path.exists(out), "| errores:", bad or "ninguno")
PY
```

---

## 16. Referencia rápida

```
Entidad        ER - Entity        v0   w=0.385n+1.4  h=1.8   name*  weak  associative
Atributo       ER - Attribute     v0   w=0.385n+2.0  h=1.8   name*  key weak_key derived multivalued
Relación       ER - Relationship  v0   w=0.385n+2.0  h=0.6w  name* left_card* right_card* identifying rotated
Línea attr.    Standard - Line    v0   conn_endpoints + connections   (conectar por 8/8, 8/12)
Participación  ER - Participation v1   orth_points orth_orient(n-1) autorouting=true total connections
Especializ.    Flowchart - Merge  v1   2.225 x 2.2   texto ES (sans/Helvetica)  flip_vertical
Texto suelto   Standard - Text    v1   text{string,font,height,pos,color,alignment} valign

* = obligatorio (si falta, Dia se cierra)
Puntos entidad:  0 TL · 1 N · 2 TR · 3 W · 4 E · 5 BL · 6 S · 7 BR · 8 centro (autogap)
Puntos rombo:    0 W · 1 NW · 2 N · 3 NE · 4 E · 5 SW · 6 S · 7 SE · 8 centro (autogap)
Puntos ES:       0-4 borde superior · 8 vértice inf. · 12 centro (autogap)
Texto:           <dia:string>#…#</dia:string>   ·   Colores #rrggbb   ·   Unidades: cm
```
