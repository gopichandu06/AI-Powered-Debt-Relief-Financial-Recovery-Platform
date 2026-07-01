import React, { useState } from 'react';
import { Shield, ChevronDown, CheckCircle, AlertTriangle, Scale, BookOpen, ExternalLink } from 'lucide-react';
import './rights.css';

const RIGHTS_CONTENT = [
  {
    id: 'rights',
    title: 'Know Your Rights as a Borrower',
    icon: <Scale size={20} />,
    points: [
      'Right to full disclosure of loan terms, interest rates, and fees before signing.',
      'Right to receive a copy of your loan agreement and repayment schedule.',
      'Right to be treated with dignity and respect by collection agents.',
      'Right to privacy regarding your financial information and debt status.',
      'Right to challenge and correct inaccurate information in your credit report.'
    ]
  },
  {
    id: 'collection',
    title: 'Debt Collection Rules (What collectors CANNOT do)',
    icon: <AlertTriangle size={20} />,
    points: [
      'Cannot call you at unreasonable hours (generally before 8 AM or after 7 PM).',
      'Cannot use abusive, threatening, or offensive language.',
      'Cannot discuss your debt with third parties (friends, relatives, employer) without your consent.',
      'Cannot make false claims about legal action, arrest, or property seizure.',
      'Cannot charge fees or interest not authorized by your original loan agreement.'
    ]
  },
  {
    id: 'negotiation',
    title: 'Negotiation Tips & Strategies',
    icon: <BookOpen size={20} />,
    points: [
      'Never ignore communication from lenders; acknowledge the debt but explain your hardship.',
      'Document everything. Keep records of all calls, emails, and letters.',
      'Do not make a partial payment until a formal settlement agreement is reached in writing.',
      'Start your negotiation offer lower than what you can actually afford to leave room for counter-offers.',
      'Request a "Pay for Delete" agreement where the lender agrees to remove the negative mark from your credit report upon payment.',
      'If the debt is very old, check the statute of limitations in your state/country before agreeing to pay.',
      'Consider offering a lump-sum payment. Lenders are often more willing to settle for a lower amount if paid all at once.'
    ]
  },
  {
    id: 'recovery',
    title: 'Financial Recovery Roadmap',
    icon: <CheckCircle size={20} />,
    points: [
      'Step 1: Assess your total debt and prioritize high-interest or secured loans.',
      'Step 2: Create a realistic survival budget cutting all non-essential expenses.',
      'Step 3: Contact lenders proactively before defaulting to ask for hardship programs.',
      'Step 4: Use our AI Settlement tool to determine the best settlement strategy.',
      'Step 5: Send professional negotiation letters proposing structured settlements.',
      'Step 6: Once settled, begin rebuilding credit slowly with a secured credit card.'
    ]
  }
];

export default function BorrowerRights() {
  const [openSection, setOpenSection] = useState('rights');

  return (
    <div className="page-container rights-page animate-fade-in">
      <div className="rights-hero card">
        <Shield size={48} className="accent" />
        <h1 className="page-title">Borrower Rights & Education</h1>
        <p className="page-subtitle">Understand your legal protections, deal with collection agents safely, and master the art of negotiation.</p>
      </div>

      <div className="important-notice">
        <AlertTriangle size={20} />
        <div>
          <strong>Disclaimer:</strong> The information provided here is for educational purposes and does not constitute formal legal advice. If you are facing severe legal action, please consult a qualified attorney.
        </div>
      </div>

      <div className="accordion-container">
        {RIGHTS_CONTENT.map(section => (
          <div key={section.id} className={`accordion-item card ${openSection === section.id ? 'open' : ''}`}>
            <button 
              className="accordion-header"
              onClick={() => setOpenSection(openSection === section.id ? null : section.id)}
            >
              <div className="accordion-title">
                {section.icon}
                <h2>{section.title}</h2>
              </div>
              <ChevronDown size={20} className="chevron" />
            </button>
            <div className="accordion-content">
              <ul>
                {section.points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      <div className="resources-section card">
        <h2>Emergency Resources</h2>
        <div className="resource-links">
          <a href="#" className="resource-link">
            <div>
              <strong>Consumer Financial Protection Bureau (CFPB)</strong>
              <span>Submit a complaint about a financial product or service.</span>
            </div>
            <ExternalLink size={16} />
          </a>
          <a href="#" className="resource-link">
            <div>
              <strong>National Foundation for Credit Counseling (NFCC)</strong>
              <span>Find a certified non-profit credit counselor.</span>
            </div>
            <ExternalLink size={16} />
          </a>
        </div>
      </div>
    </div>
  );
}
