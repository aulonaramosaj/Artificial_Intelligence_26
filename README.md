# Detyra e parë semestrale – Teknikat e Painformuara të Kërkimit

| # | Problemi | Algoritmi | Skedari |
|---|----------|-----------|---------|
| 1 | Social Golfers | DFS me Backtracking | [1_social_golfers/social_golfers.py](1_social_golfers/social_golfers.py) |
| 2 | Sudoku (Easy / Medium / Hard) | BFS me Backtracking | [2_sudoku/sudoku_bfs.py](2_sudoku/sudoku_bfs.py) |
| 3 | Latin Square | IDDFS me Backtracking | [3_latin_square/latin_square_iddfs.py](3_latin_square/latin_square_iddfs.py) |
| 4 | Search Trees: 8-Puzzle, Missionaries & Cannibals, Rotating Workforce Scheduling | Vizatim me dorë | [4_search_trees/](4_search_trees/) |

```bash
python3 1_social_golfers/social_golfers.py            # 32 lojtarë, 8 grupe x 4
python3 2_sudoku/sudoku_bfs.py                        # easy, medium, hard
python3 3_latin_square/latin_square_iddfs.py 5        # katror latin 5x5
```

### Ndërfaqja grafike (UI)

```bash
python3 app.py
```

[app.py](app.py) (Tkinter) hap një dritare me 3 faqe. Çdo faqe thërret të njëjtat algoritme si programet në konsolë:

- **Social Golfers** – parametrat g, p, w → orari në tabelë, log-u i kërkimit dhe kontrolli i partnerëve të një lojtari.
- **Sudoku** – Easy / Medium / Hard (ose Sudoku i shkruar me dorë në tabelë); animacion i zgjerimeve të BFS (thellësia dhe madhësia e radhës).
- **Latin Square** – IDDFS, tabela e iteracioneve (kufiri, nyje, rezultati), katrori me ngjyra dhe butoni **Ndalo** (n maksimal në UI = 7).

---

## 1. Social Golfers – DFS me Backtracking

### Problemi

32 lojtarë luajnë golf një herë në javë, në 8 grupe me nga 4 lojtarë.
Rregulli: **dy lojtarë që kanë luajtur një herë bashkë nuk guxojnë të jenë më në të njëjtin grup.**
Pyetja: **për sa javë mund të vazhdohet kështu?**

Në përgjithësi: `n = g × p` lojtarë, `g` grupe me nga `p` lojtarë, për `w` javë.

```bash
python3 1_social_golfers/social_golfers.py          # gjen numrin maksimal të javëve
python3 1_social_golfers/social_golfers.py -w 5     # saktësisht 5 javë
```

### Modelimi

| | |
|---|---|
| **Gjendja** | orari i plotësuar pjesërisht |
| **Gjendja fillestare** | orari bosh |
| **Veprimi** | vendos një lojtar në pozitën e radhës të lirë |
| **Qëllimi** | të gjitha pozitat plot, pa shkelur rregullat |

### Reprezentimi

| | |
|---|---|
| **Variabla** | `x[java][grupi][pozita]`, lojtari në atë vend (32 variabla për javë) |
| **Domain** | `{0, 1, …, 31}`, numri i lojtarit |
| **Kufizimi C1** | çdo lojtar luan saktësisht një herë në javë |
| **Kufizimi C2** | dy lojtarë takohen në të njëjtin grup më së shumti një herë |

### Objective function

```
f(S) = sa herë takohen përsëri dy lojtarë që kanë luajtur tashmë bashkë
```

Orari është i vlefshëm kur **f(S) = 0**. Qëllimi është të gjendet `w` sa më i madh me f(S) = 0.

**Kufiri i sipërm:** çdo javë lojtari takon 3 lojtarë të rinj. Ka gjithsej 31 lojtarë të tjerë, pra `w ≤ 31 / 3 = 10` javë.

### Landscape

Landscape = sa orare të mundshme ekzistojnë gjithsej.

**1. Nga reprezentimi:** çdo variabël mund të marrë çdo vlerë nga domain-i.

```
32^(32·w)        → për 1 javë: 32³² ≈ 1.46·10⁴⁸
```

**2. Oraret reale:** renditja brenda grupit dhe renditja e grupeve nuk kanë rëndësi
(`{0,1,2,3}` = `{3,2,1,0}`), kështu që pjesëtojmë me `(4!)⁸ · 8!`:

```
(32! / ((4!)⁸ · 8!))^w   → për 1 javë ≈ 5.93·10¹⁹, për 5 javë ≈ 7.32·10⁹⁸
```

Shembull i vogël: 4 lojtarë në 2 grupe me nga 2 kanë 4⁴ = 256 mundësi,
por vetëm **3** ndarje reale: `{01|23}`, `{02|13}`, `{03|12}`.

### Implementimi

**DFS e thjeshtë me backtracking**, pa heuristikë. Pozitat plotësohen me radhë
(java → grupi → pozita) dhe lojtarët provohen me radhë 0, 1, 2, …

1. merr pozitën e radhës të lirë;
2. provo lojtarin e radhës që nuk i shkel C1 dhe C2;
3. vazhdo me pozitën tjetër (zbrit më thellë);
4. nëse ngec, hiqe lojtarin e fundit (**backtracking**) dhe provo tjetrin.

**Thyerja e simetrisë:** brenda grupit lojtarët janë në rend rritës, dhe grupi fillon
me lojtarin më të vogël të lirë. Kjo nuk është heuristikë: vetëm siguron që i njëjti
orar të mos provohet disa herë me renditje tjetër.

### Rezultatet

| Javë | Rezultati |
|---|---|
| 1–5 | gjen menjëherë (161 nyje, pa asnjë backtrack) |
| 6 | nuk gjen brenda kufirit kohor (> 14 milion nyje) |

**Përgjigja:** DFS arrin **5 javë**. Kufiri teorik është 10 javë, dhe dihet që 10 javë
janë të mundshme, por ajo zgjidhje është gjetur me matematikë dhe jo me kërkim të verbër.
Hapësira është shumë e madhe (≈ 10⁹⁹ orare vetëm për 5 javë) që DFS e painformuar të arrijë më larg.

---

## 2. Sudoku – BFS me Backtracking

### Problemi

Sudoku është një tabelë 9×9 e ndarë në 9 kuti 3×3. Disa numra janë të dhënë që në fillim,
qelizat e tjera janë bosh. Duhet t'i mbushësh me numrat 1–9 ashtu që çdo numër të paraqitet
**saktësisht një herë** në çdo **rresht**, në çdo **kolonë** dhe në çdo **kuti 3×3**.

Programi ka tri nivele: **Easy** (40 numra të dhënë), **Medium** (32) dhe **Hard** (21).
Sa më pak numra të dhënë, aq më shumë mundësi duhen provuar.

```bash
python3 2_sudoku/sudoku_bfs.py          # zgjidh të tri nivelet
python3 2_sudoku/sudoku_bfs.py hard     # vetëm një nivel
```

### Modelimi

| | |
|---|---|
| **Gjendja** | tabela e plotësuar pjesërisht |
| **Gjendja fillestare** | Sudoku i dhënë |
| **Veprimi** | shkruaj një numër të lejuar në qelizën e radhës bosh |
| **Qëllimi** | nuk mbetet asnjë qelizë bosh |

### Reprezentimi

| | |
|---|---|
| **Variabla** | çdo qelizë bosh `X[rreshti][kolona]` |
| **Domain** | `{1, 2, …, 9}` |
| **Kufizimet** | numra të ndryshëm në çdo rresht, kolonë dhe kuti 3×3 (27 kufizime) |

### Objective function

```
f = (sa çifte qelizash në të njëjtin rresht/kolonë/kuti kanë numër të njëjtë) + (sa qeliza janë bosh)
```

Sudoku është i zgjidhur kur **f = 0**: asnjë rregull nuk shkelet dhe asnjë qelizë nuk është bosh.

### Landscape

Landscape = sa tabela të mundshme ekzistojnë. Çdo qelizë bosh mund të marrë 9 vlera,
pra me `k` qeliza bosh kemi `9^k` mundësi:

| Niveli | Qeliza bosh | Mundësi |
|---|---|---|
| Easy | 41 | 9⁴¹ ≈ 1.33·10³⁹ |
| Medium | 49 | 9⁴⁹ ≈ 5.73·10⁴⁶ |
| Hard | 60 | 9⁶⁰ ≈ 1.80·10⁵⁷ |

Nëse për secilën qelizë heqim numrat që i kanë tashmë fqinjët e saj, hapësira zvogëlohet shumë,
p.sh. Easy bëhet ≈ 2.67·10¹⁵.

### Implementimi

**BFS e thjeshtë**, pa heuristikë. Përdor një **radhë (FIFO)**: gjendja që hyn e para, del e para.
Kështu pema eksplorohet **nivel pas niveli**. Qelizat plotësohen rresht pas rreshti,
dhe numrat provohen me radhë 1, 2, …, 9.

1. merr gjendjen e parë nga radha;
2. nëse nuk ka qeliza bosh, kjo është zgjidhja;
3. gjej qelizën e parë bosh dhe numrat e lejuar për të;
4. nëse nuk ka asnjë numër të lejuar, gjendja hidhet (**backtracking**);
5. përndryshe, shto në radhë një gjendje të re për secilin numër të lejuar.

**Backtracking te BFS:** BFS nuk kthehet prapa si DFS. Këtu backtracking do të thotë
që degët pa dalje hidhen, dhe kërkimi vazhdon me gjendjet e tjera në radhë.

### Rezultatet

| Niveli | Nyje të zgjeruara | Kohë |
|---|---|---|
| Easy | 1 256 | 0.003 s |
| Medium | 33 253 | 0.1 s |
| Hard | 2 068 781 | ~5 s |

Të tri zgjidhen me **f = 0**. Te Hard-i radha arrin deri në 356 812 gjendje njëkohësisht
(~320 MB memorie). Kjo është dobësia e njohur e BFS-së: i mban në memorie të gjitha gjendjet
e një niveli.

---

## 3. Latin Square – IDDFS me Backtracking

### Problemi

Katrori latin është një tabelë n×n e mbushur me numrat 1..n, ashtu që çdo numër
paraqitet **saktësisht një herë** në çdo **rresht** dhe në çdo **kolonë**.
Shembull për n = 3:

```
1 2 3
2 3 1
3 1 2
```

Për çdo n ka shumë katrorë latinë (për n = 5 janë 161 280), dhe çdonjëri është përgjigje e saktë.

```bash
python3 3_latin_square/latin_square_iddfs.py 5     # katror latin 5×5
```

### Modelimi

| | |
|---|---|
| **Gjendja** | tabela e mbushur pjesërisht (qelizat mbushen rresht pas rreshti) |
| **Gjendja fillestare** | rreshti i parë dhe kolona e parë `1..n`, pjesa tjetër bosh |
| **Veprimi** | shkruaj një numër të lejuar në qelizën e radhës bosh |
| **Qëllimi** | të gjitha qelizat plot |

Thellësia në pemë = sa qeliza janë mbushur.

### Reprezentimi

| | |
|---|---|
| **Variabla** | çdo qelizë `X[rreshti][kolona]` |
| **Domain** | `{1, 2, …, n}` |
| **Kufizimet** | numra të ndryshëm në çdo rresht dhe në çdo kolonë (2n kufizime) |

**Thyerja e simetrisë:** rreshti i parë dhe kolona e parë fiksohen në `1..n`. Kjo lejohet,
sepse çdo katror latin mund të "riemërtohet" kështu. Nuk është heuristikë: vetëm largon
katrorët që janë i njëjti katror me emra të tjerë. Për n = 5 mbeten 16 qeliza në vend të 25.

### Objective function

```
f = sa numra përsëriten në rreshta + sa numra përsëriten në kolona
```

Tabela është katror latin kur **f = 0**.

### Landscape

Landscape = sa tabela të mundshme ekzistojnë. Çdo qelizë mund të marrë n vlera,
pra kemi `n^(n²)` mundësi:

| n | Mundësi `n^(n²)` | Prej tyre katrorë latinë |
|---|---|---|
| 4 | 4.29·10⁹ | 576 |
| 5 | 2.98·10¹⁷ | 161 280 |
| 6 | 1.03·10²⁸ | 812 851 200 |

### Implementimi

**IDDFS** = DFS me kufi thellësie, e përsëritur me kufi **0, 1, 2, …** derisa të gjendet zgjidhja.
Pa heuristikë: qelizat mbushen rresht pas rreshti dhe numrat provohen me radhë 1, 2, …, n.

1. fillo me kufi = 0;
2. ekzekuto DFS që nuk shkon më thellë se kufiri;
   - provo numrin e radhës të lejuar në qelizën e radhës;
   - nëse ngec, hiqe numrin e fundit (**backtracking**) dhe provo tjetrin;
3. nëse DFS e gjeti zgjidhjen → ndalo (`found`);
4. nëse u ndal te kufiri → rrite kufirin për 1 dhe përsërit (`cutoff`).

### Rezultatet

| n | Iteracione | Nyje | Kohë |
|---|---|---|---|
| 5 | 17 | 4 914 | 0.003 s |
| 6 | 26 | 1 194 077 | 0.8 s |
| 7 | – | > 750 milion | nuk mbaron (> 9 min) |

**Pse ngec për n ≥ 7:** zgjidhja është gjithmonë në fund të pemës (kur të gjitha qelizat janë plot).  
Prandaj çdo iteracion para të fundit e eksploron gjithë pemën kot. IDDFS është e dobishme  
kur zgjidhja mund të jetë afër, p.sh. kur kërkohet rruga më e shkurtër.  
Teorikisht katror latin ekziston për çdo n, por me IDDFS kufiri praktik është **n = 6**.

---

## 4. Search Trees

Për secilin problem është vizatuar me dorë pema e kërkimit: nga gjendja fillestare, me të gjitha veprimet e mundshme, nivel pas niveli, deri te qëllimi.

**Simbolet në fletë:** ✗ = gjendje e pavlefshme (shkel rregullat, nuk zgjerohet), ↺ = gjendje e përsëritur (është parë më herët, nuk zgjerohet), qëllimi është i rrethuar.

### 8-Puzzle – [8_Puzzles.pdf](4_search_trees/8_Puzzles.pdf)
| | |
|---|---|
| **Gjendja** | tabela 3×3 me pllakat 1–8 dhe një vend bosh |
| **Fillestare** | `1 2 3 / 4 _ 6 / 7 5 8` |
| **Qëllimi** | `1 2 3 / 4 5 6 / 7 8 _` |
| **Veprimet** | vendi bosh lëviz Up, Down, Left, Right |

Pema ndërtohet me BFS. Lëvizja që e kthen vendin bosh te prindi nuk vizatohet. Qëllimi arrihet në nivelin 2 me **Down → Right**.

### Missionaries and Cannibals – [Missionaries_and_Cannibals.pdf](4_search_trees/Missionaries_and_Cannibals.pdf)
| | |
|---|---|
| **Gjendja** | `(M, K, B)`: misionarët dhe kanibalët në bregun e majtë, dhe ana e varkës (L = majtas, D = djathtas) |
| **Fillestare** | `(3,3,L)` |
| **Qëllimi** | `(0,0,D)` |
| **Veprimet** | varka mbart `1M`, `2M`, `1K`, `2K` ose `1M1K` |
| **Rregulli** | në asnjë breg kanibalët nuk janë më shumë se misionarët (kur ka misionarë) |

Pema ndërtohet me BFS. Gjendjet ✗ dhe ↺ nuk zgjerohen. Qëllimi arrihet në nivelin 11 (11 kalime).

### Rotating Workforce Scheduling – [Rotating_Workforce_Schedule.pdf](4_search_trees/Rotating_Workforce_Schedule.pdf)
RWS i vërtetë është shumë i madh për t'u vizatuar, prandaj përdoret një shembull i vogël.

| | |
|---|---|
| **Shembulli** | 3 punëtorë (rreshtat), 3 ditë (kolonat): e hënë, e martë, e mërkurë |
| **Kërkesa** | çdo ditë: 1 D (dita), 1 N (nata), 1 – (pushim) |
| **Rregulli** | pas N nuk vjen D të nesërmen, edhe nga dita e fundit e një rreshti te dita e parë e rreshtit tjetër (rrotullimi) |
| **Gjendja** | orari i mbushur pjesërisht, ditë pas dite |
| **Fillestare** | orari bosh |
| **Veprimi** | zgjidh ndërrimet e ditës së radhës për të 3 punëtorët (6 mundësi) |
| **Qëllimi** | 3 ditët plot, pa asnjë N → D |

Në çdo nivel zgjerohet vetëm nyja e parë; të tjerat zgjerohen njësoj. Qëllimi:

```
D D D
N N N
– – –
```
