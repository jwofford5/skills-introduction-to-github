from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# Margins
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.25)
    section.right_margin = Inches(1.25)

# Default style
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(11)

def add_horizontal_rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def add_section_header(doc, text):
    add_horizontal_rule(doc)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.name = 'Times New Roman'
    return p

def add_name_header(doc, name):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(name)
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = 'Times New Roman'
    return p

def add_contact_line(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.name = 'Times New Roman'
    return p

def add_entry(doc, left, right=None, bold_left=False, indent=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    if indent:
        p.paragraph_format.left_indent = Inches(0.25)
    if right:
        # Use a tab stop for right-aligned date
        tab = OxmlElement('w:tab')
        pPr = p._p.get_or_add_pPr()
        tabs = OxmlElement('w:tabs')
        tabStop = OxmlElement('w:tab')
        tabStop.set(qn('w:val'), 'left')
        tabStop.set(qn('w:pos'), '720')  # 0.5 inch
        tabs.append(tabStop)
        pPr.append(tabs)
        date_run = p.add_run(left + '\t')
        date_run.font.name = 'Times New Roman'
        date_run.font.size = Pt(11)
        body_run = p.add_run(right)
        body_run.font.name = 'Times New Roman'
        body_run.font.size = Pt(11)
        if bold_left:
            body_run.bold = True
    else:
        run = p.add_run(left)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        if bold_left:
            run.bold = True
    return p

def add_bullet(doc, text, sub=False):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.5 if not sub else 0.75)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    return p

def add_para(doc, text, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    return p

def add_bold_intro(doc, bold_text, normal_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(bold_text)
    r1.bold = True
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r2 = p.add_run(normal_text)
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11)
    return p

# ── NAME & CONTACT ──────────────────────────────────────────────
add_name_header(doc, 'Chester Lee McMillion')
add_contact_line(doc, 'lj.mcmillion@icloud.com  |  714.642.1313')
add_contact_line(doc, 'Los Angeles, California')

# ── RESEARCH INTERESTS ──────────────────────────────────────────
add_section_header(doc, 'Research Interests')
add_para(doc,
    'Counterterrorism policy and practice; transatlantic security cooperation; '
    'critical incident command and interagency coordination; comparative police '
    'and military special operations doctrine; security governance for major '
    'international events.')

# ── EDUCATION ───────────────────────────────────────────────────
add_section_header(doc, 'Education')

add_bold_intro(doc, 'Fulbright Scholar / Research Fellowship', '  |  London, England  |  September 2011 – March 2012')
add_para(doc,
    'Conducted independent research on counterterrorism and critical incident '
    'response throughout the United Kingdom. Embedded and liaised with '
    'counterterror police and military special forces units across England, '
    'Scotland, and Wales. Sponsored by the U.S. Department of State Bureau '
    'of Educational and Cultural Affairs.', space_after=6)

add_bold_intro(doc, 'Foundation for Senior Leaders', '  |  National Police College, Bramshill, England  |  January 2012')
add_para(doc, 'Executive Module, Business Module, and Professional Policing Module', space_after=6)

add_bold_intro(doc, 'Master of Public Administration (MPA)', '  |  University of Southern California, Los Angeles, CA  |  December 2002')
add_para(doc, 'Certificate of Merit, Outstanding Master\'s Graduate Student  |  Pi Alpha Alpha National Honor Society', space_after=6)

add_bold_intro(doc, 'Bachelor of Arts, Political Science', '  |  Union Institute, Los Angeles, CA  |  September 1993')
add_para(doc, 'Emphasis in International Security and International Relations', space_after=6)

add_bold_intro(doc, 'Instructor Development Course', '  |  University of California, Los Angeles  |  August 1993')
add_para(doc, '', space_after=2)

add_bold_intro(doc, 'Delinquency Control Institute, 110th Class', '  |  University of Southern California  |  February 2000')

# ── INTERNATIONAL AFFAIRS & RESEARCH EXPERIENCE ─────────────────
add_section_header(doc, 'International Affairs and Research Experience')

add_bold_intro(doc, 'Foreign Liaison and International Security Advisor', '  |  1996 – Present')
add_para(doc,
    'Sustained, senior-level engagement with foreign law enforcement, military, '
    'and government counterparts across the United Kingdom, France, Norway, and '
    'the United Arab Emirates. Work encompasses counterterrorism best practices, '
    'threat trend analysis, tactical doctrine exchange, policy coordination, '
    'cultural awareness, and diplomatic response protocols.')
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(2)
p.paragraph_format.space_after = Pt(2)
r = p.add_run('Selected contributions:')
r.italic = True
r.font.name = 'Times New Roman'
r.font.size = Pt(11)
add_bullet(doc, 'Organized and led major incident debriefs and security planning for the London Olympics (2012), Paris Olympics (2024), and the upcoming Los Angeles Olympics (2028), coordinating across national and international stakeholders.')
add_bullet(doc, 'Facilitated bilateral personnel exchanges between LAPD SWAT and allied special operations units to advance shared doctrine and interoperability.')
add_bullet(doc, 'Provided leadership development training in critical incident command and interagency coordination to international partners.')
add_bullet(doc, 'Recognized by the U.S. Department of State as an International Exchange Alumni for contributions to public safety diplomacy.')

# ── PROFESSIONAL RESEARCH & ANALYSIS ────────────────────────────
add_section_header(doc, 'Professional Research and Analysis')

add_bold_intro(doc, 'Expert Witness and Law Enforcement Analyst', '  |  Independent Consultant  |  2008 – Present')
add_para(doc,
    'Retained by law enforcement agencies and legal counsel to provide expert '
    'analysis and testimony in civil litigation. Each engagement requires in-depth '
    'examination of agency policies and procedures, incident reconstruction, and '
    'assessment of compliance with applicable case law and professional standards. '
    'Analysis is synthesized into formal written reports — typically Federal Rule '
    '26 expert reports — submitted in federal and state proceedings.')
add_bullet(doc, 'Research scope encompasses use-of-force doctrine, tactical decision-making, pursuit policy, officer conduct, and supervisory responsibility.')
add_bullet(doc, 'Findings are translated into structured written analysis accessible to legal, judicial, and lay audiences.')

# ── TEACHING EXPERIENCE ──────────────────────────────────────────
add_section_header(doc, 'Teaching Experience')

add_bold_intro(doc, 'Instructor', '  |  National Tactical Officers Association (NTOA)')
add_bullet(doc, 'Basic and Advanced SWAT Tactics')
add_bullet(doc, 'Crisis Negotiations')
add_bullet(doc, 'SWAT Team Leadership')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Instructor', '  |  California Association of Tactical Officers (CATO)')
add_bullet(doc, 'SWAT Team Leadership')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Instructor', '  |  Blackwater Training, USA')
add_bullet(doc, 'Basic and Advanced SWAT Tactics')
add_bullet(doc, 'Crisis Negotiations')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Recruit and In-Service Instructor', '  |  LAPD Training Division, Firearms Training Unit  |  1993 – 1994')

# ── PROFESSIONAL EXPERIENCE ──────────────────────────────────────
add_section_header(doc, 'Professional Experience')

add_bold_intro(doc, 'Los Angeles Police Department', '  |  1988 – Present')
add_para(doc, 'California POST Certificates: Advanced, Supervisory, and Management', space_after=6)

add_bold_intro(doc, 'Lieutenant II, SWAT Team Commander', '  |  Metropolitan Division, SWAT  |  2015 – Present')
add_bullet(doc, 'Command one of two leadership positions for LAPD SWAT, a 68-person full-time unit averaging 150 deployments annually — approximately 130 spontaneous (armed barricade, hostage rescue, suicidal subjects) and 20 high-risk warrant operations.')
add_bullet(doc, 'Evaluate and approve all response tactics; maintain accountability to chain of command for deployment decisions consistent with contemporary use-of-force standards.')
add_bullet(doc, 'Over a 10-year period, 92% of approximately 1,500 incidents were resolved without use of force; only 1.48% required deadly force — reflecting a commitment to de-escalation and tactical restraint.')
add_bullet(doc, 'Manage personnel development, employee assessments, misconduct investigations, and inner-platoon promotions.')
add_bullet(doc, 'Administer multiple funding streams including city budget allocations, grants, and donations, ensuring full compliance and absence of conflict of interest.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Lieutenant II, Gang Impact Team Commander', '  |  77th Street Area  |  2013 – 2015')
add_bullet(doc, 'Led integrated unit comprising Gang Enforcement, Gang Investigations (detectives), and Narcotics Enforcement details.')
add_bullet(doc, 'Coordinated with local, state, and federal agencies to address criminal street gang activity; served as Acting Patrol Commanding Officer in absence of the Division Captain.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Lieutenant I, Patrol Watch Commander', '  |  Newton Patrol Division  |  2012 – 2013')
add_bullet(doc, 'Served as incident commander for major events including officer-involved shootings, pursuit management, and large-scale tactical situations.')
add_bullet(doc, 'Provided administrative oversight for uses of force, risk management, and chain-of-command notifications.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Sergeant II, SWAT Squad Leader', '  |  Metropolitan Division, SWAT  |  2009 – 2012')
add_bullet(doc, 'Supervised specialty cadres including snipers, lead climbers, tactical waterborne divers, firearms instructors, and crisis negotiators.')
add_bullet(doc, 'Led supervision and documentation for all platoon deployments — spontaneous and preplanned — and daily training operations.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Sergeant I / SWAT Tactical Waterborne Diving Supervisor', '  |  77th Street Patrol Division  |  2007 – 2008')
add_bullet(doc, 'Served as the only LAPD sergeant qualified in tactical waterborne protocols; retained in ancillary SWAT role while fulfilling post-promotion patrol requirement.')
add_bullet(doc, 'Supervised the 12-person Tactical Waterborne (TWB) cadre responsible for SWAT operations across 52 miles of Los Angeles waterfront, including the Port of Los Angeles/Long Beach — the third-largest container facility in the world.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'SWAT Officer / Element Leader (Police Officer 3 / 3+1)', '  |  Metropolitan Division, SWAT  |  1996 – 2007')
add_bullet(doc, 'Served as element member (1996–2003) and element leader (2003–2007) in full-time, 60-officer unit.')
add_bullet(doc, 'Specializations: sniper, lead climber, tactical waterborne diver, firearms instructor, military and foreign liaison.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Security Aide to the Chief of Police', '  |  Office of the Chief of Police  |  1999 – 2002')
add_bullet(doc, 'Provided personal protection for Chief Bernard C. Parks and Chief Martin Pomeroy during all public engagements.')
add_bullet(doc, 'Conducted threat assessments, site surveys, route planning, and liaised with local, state, federal, and international law enforcement and government entities.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Metropolitan Division, C Platoon (Police Officer 3)', '  |  1994 – 1996')
add_bullet(doc, 'Responded to riots, natural disasters, and civil disturbances. Supplemented U.S. Secret Service and Department of State in dignitary protection.')

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
add_bold_intro(doc, 'Field Officer', '  |  Southeast and Rampart Patrol Divisions  |  1988 – 1994')
add_bullet(doc, 'Patrol, narcotics, Predator Apprehension Team, and Special Problems Unit.')

# ── MILITARY SERVICE ─────────────────────────────────────────────
add_section_header(doc, 'Military Service')

add_bold_intro(doc, 'United States Coast Guard Reserve', '  |  Petty Officer  |  1984 – 1992')
add_bullet(doc, 'Marine Safety Office, Port of Los Angeles/Long Beach: drug interdiction, search and rescue, vessel inspections, hazardous materials investigations, and small arms instruction.')
add_bullet(doc, 'Port Security "A" School, Yorktown, Virginia (1985); Recruit Training, Cape May, New Jersey (1984).')
add_bullet(doc, 'Awards: National Defense Service Medal; Coast Guard Reserve Good Conduct Medal with Bronze Star Device.')

# ── PROFESSIONAL AFFILIATIONS ────────────────────────────────────
add_section_header(doc, 'Professional Affiliations and Memberships')

affiliations = [
    'International Exchange Alumni, U.S. Department of State (2012 – Present)',
    'Chartered Management Institute, England (2012 – Present)',
    'Royal Society for the Encouragement of Arts, Manufactures and Commerce, England (2011 – Present)',
    'Pi Alpha Alpha – National Honor Society for Public Affairs and Administration (2002 – Present)',
    'University of Southern California Alumni Association (2002 – Present)',
    'American Mensa (2000 – Present)',
    'Professional Association of Diving Instructors, Divemaster #178558 (2000 – Present)',
    'National Tactical Officers Association (1996 – Present)',
    'California Association of Tactical Officers (1996 – Present)',
    'Fraternal Order of Police, Lodge 1 (1990 – Present)',
    'American Legion, Post 291 (2020 – Present)',
]
for a in affiliations:
    add_bullet(doc, a)

# ── HONORS & COMMENDATIONS ───────────────────────────────────────
add_section_header(doc, 'Honors and Commendations')
add_bullet(doc, 'Fulbright Scholarship / Research Fellowship, U.S. Department of State (2011–2012)')
add_bullet(doc, 'Certificate of Merit, Outstanding Master\'s Graduate Student, University of Southern California (2002)')
add_bullet(doc, 'Los Angeles Police Department Major Commendations (8)')
add_bullet(doc, 'Los Angeles Police Department Minor Commendations (130+)')

filename = 'resume_Chester_McMillion.docx'
doc.save(filename)
print(f'Saved: {filename}')
