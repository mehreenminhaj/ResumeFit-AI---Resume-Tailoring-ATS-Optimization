import { Document, Paragraph, TextRun, HeadingLevel, Packer, AlignmentType } from 'docx';
import { ResumeData, TailoredResumeData } from '../src/types/resume.js';

export async function generateDocxResume(
  baseResume: ResumeData,
  tailored: TailoredResumeData
): Promise<Buffer> {
  const children: Paragraph[] = [];

  // Header: Name
  children.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 100 },
      children: [
        new TextRun({
          text: baseResume.fullName || 'Candidate Resume',
          bold: true,
          size: 32, // 16pt
          font: 'Arial',
        }),
      ],
    })
  );

  // Contact line
  const contactParts: string[] = [];
  if (baseResume.email) contactParts.push(baseResume.email);
  if (baseResume.phone) contactParts.push(baseResume.phone);
  if (baseResume.location) contactParts.push(baseResume.location);
  if (baseResume.linkedin) contactParts.push(baseResume.linkedin);
  if (baseResume.github) contactParts.push(baseResume.github);

  if (contactParts.length > 0) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [
          new TextRun({
            text: contactParts.join('  •  '),
            size: 20, // 10pt
            font: 'Arial',
            color: '555555',
          }),
        ],
      })
    );
  }

  // Section 1: Professional Summary
  children.push(
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 100 },
      children: [
        new TextRun({
          text: 'PROFESSIONAL SUMMARY',
          bold: true,
          size: 22,
          font: 'Arial',
        }),
      ],
    })
  );

  children.push(
    new Paragraph({
      spacing: { after: 200 },
      children: [
        new TextRun({
          text: tailored.tailoredSummary || baseResume.summary,
          size: 21,
          font: 'Arial',
        }),
      ],
    })
  );

  // Section 2: Technical Skills
  children.push(
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 100 },
      children: [
        new TextRun({
          text: 'TECHNICAL & PROFESSIONAL SKILLS',
          bold: true,
          size: 22,
          font: 'Arial',
        }),
      ],
    })
  );

  if (tailored.prioritizedSkills && tailored.prioritizedSkills.length > 0) {
    for (const group of tailored.prioritizedSkills) {
      children.push(
        new Paragraph({
          spacing: { after: 80 },
          children: [
            new TextRun({
              text: `${group.category}: `,
              bold: true,
              size: 21,
              font: 'Arial',
            }),
            new TextRun({
              text: group.skills.join(', '),
              size: 21,
              font: 'Arial',
            }),
          ],
        })
      );
    }
  } else {
    children.push(
      new Paragraph({
        spacing: { after: 150 },
        children: [
          new TextRun({
            text: baseResume.technicalSkills.join(', '),
            size: 21,
            font: 'Arial',
          }),
        ],
      })
    );
  }

  // Section 3: Professional Experience
  children.push(
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 250, after: 120 },
      children: [
        new TextRun({
          text: 'WORK EXPERIENCE',
          bold: true,
          size: 22,
          font: 'Arial',
        }),
      ],
    })
  );

  const tailoredExpMap = new Map<string, string[]>();
  tailored.tailoredExperience.forEach(te => tailoredExpMap.set(te.id, te.bullets));

  for (const exp of baseResume.experience) {
    const dates = [exp.startDate, exp.endDate || (exp.current ? 'Present' : '')].filter(Boolean).join(' - ');
    
    // Role & Company Header
    children.push(
      new Paragraph({
        spacing: { before: 140, after: 40 },
        children: [
          new TextRun({
            text: exp.role,
            bold: true,
            size: 21,
            font: 'Arial',
          }),
          new TextRun({
            text: `  |  ${exp.company}`,
            bold: false,
            italics: true,
            size: 21,
            font: 'Arial',
          }),
          ...(dates ? [
            new TextRun({
              text: `  (${dates})`,
              size: 19,
              font: 'Arial',
              color: '666666',
            }),
          ] : []),
        ],
      })
    );

    const bulletsToUse = tailoredExpMap.get(exp.id) || exp.bullets;
    for (const b of bulletsToUse) {
      children.push(
        new Paragraph({
          bullet: { level: 0 },
          spacing: { after: 60 },
          children: [
            new TextRun({
              text: b,
              size: 20,
              font: 'Arial',
            }),
          ],
        })
      );
    }
  }

  // Section 4: Projects (if present)
  if (baseResume.projects && baseResume.projects.length > 0) {
    children.push(
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 250, after: 120 },
        children: [
          new TextRun({
            text: 'KEY PROJECTS',
            bold: true,
            size: 22,
            font: 'Arial',
          }),
        ],
      })
    );

    for (const proj of baseResume.projects) {
      const techStr = proj.technologies && proj.technologies.length > 0 ? ` (${proj.technologies.join(', ')})` : '';
      children.push(
        new Paragraph({
          spacing: { before: 120, after: 40 },
          children: [
            new TextRun({
              text: proj.title,
              bold: true,
              size: 21,
              font: 'Arial',
            }),
            new TextRun({
              text: techStr,
              italics: true,
              size: 20,
              font: 'Arial',
              color: '555555',
            }),
          ],
        })
      );

      if (proj.bullets && proj.bullets.length > 0) {
        for (const b of proj.bullets) {
          children.push(
            new Paragraph({
              bullet: { level: 0 },
              spacing: { after: 50 },
              children: [
                new TextRun({
                  text: b,
                  size: 20,
                  font: 'Arial',
                }),
              ],
            })
          );
        }
      } else if (proj.description) {
        children.push(
          new Paragraph({
            spacing: { after: 80 },
            children: [
              new TextRun({
                text: proj.description,
                size: 20,
                font: 'Arial',
              }),
            ],
          })
        );
      }
    }
  }

  // Section 5: Education
  if (baseResume.education && baseResume.education.length > 0) {
    children.push(
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 250, after: 120 },
        children: [
          new TextRun({
            text: 'EDUCATION',
            bold: true,
            size: 22,
            font: 'Arial',
          }),
        ],
      })
    );

    for (const edu of baseResume.education) {
      const details = [edu.degree, edu.institution, edu.graduationYear].filter(Boolean).join('  •  ');
      children.push(
        new Paragraph({
          spacing: { after: 80 },
          children: [
            new TextRun({
              text: details,
              size: 21,
              font: 'Arial',
            }),
          ],
        })
      );
    }
  }

  // Section 6: Certifications
  if (baseResume.certifications && baseResume.certifications.length > 0) {
    children.push(
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 },
        children: [
          new TextRun({
            text: 'CERTIFICATIONS & LICENSES',
            bold: true,
            size: 22,
            font: 'Arial',
          }),
        ],
      })
    );

    children.push(
      new Paragraph({
        spacing: { after: 100 },
        children: [
          new TextRun({
            text: baseResume.certifications.join(', '),
            size: 21,
            font: 'Arial',
          }),
        ],
      })
    );
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 720, // 0.5 in
              right: 720,
              bottom: 720,
              left: 720,
            },
          },
        },
        children,
      },
    ],
  });

  return await Packer.toBuffer(doc);
}
