'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import RetroGrid from "@/components/ui/retro-grid"; // Ensure this import is correct


const MagicCard = ({ children, className = '' }) => (
  <motion.div
    className={`bg-white rounded-lg shadow-lg p-6 ${className}`}
    whileHover={{ scale: 1.05, boxShadow: '0 8px 30px rgba(0,0,0,0.12)' }}
    transition={{ type: 'spring', stiffness: 300 }}
  >
    {children}
  </motion.div>
)

const MagicButton = ({ children, className = '', ...props }) => (
  <motion.button
    className={`px-6 py-2 rounded-full font-semibold ${className}`}
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    {...props}
  >
    {children}
  </motion.button>
)

export function BlockPage() {
  const [activeArea, setActiveArea] = useState(null)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveArea((prev) => (prev === 2 ? 0 : prev + 1))
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const areas = [
    {
      title: "Mental Health",
      description: "Empowering Minds, Breaking Barriers. We're committed to reshaping how society perceives mental health by encouraging open, judgment-free conversations.",
    },
    {
      title: "Child Development",
      description: "Supporting the Next Generation's Journey. Our holistic child development initiatives nurture children from their primary years all the way to their career paths.",
    },
    {
      title: "Women's Empowerment",
      description: "Enabling Women to Lead and Thrive. We provide essential training and resources that empower women economically and socially.",
    },
  ]

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <RetroGrid className="z-0" angle={65} />
        <div className="container mx-auto px-4 py-20 relative z-10">
          <motion.h1 
            className="text-4xl md:text-6xl font-bold mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            Vikasalaya Foundation
          </motion.h1>
          
          <motion.p 
            className="text-lg md:text-xl mb-8 max-w-3xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Vikasalaya Foundation is dedicated to holistic development with a strong focus on mental health, child welfare, and women's empowerment. Our initiatives aim to break down societal barriers, empower individuals, and inspire positive change, building a brighter future for communities across India.
          </motion.p>
          <motion.div 
            className="flex flex-wrap gap-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <MagicButton className="bg-white text-green-600 hover:bg-gray-100">
              <Link href="/donate">Donate</Link>
            </MagicButton>
            <MagicButton className="border-2 border-white text-white hover:bg-white hover:text-green-600">
              <Link href="/get-involved">Get Involved</Link>
            </MagicButton>
          </motion.div>
        </div>
      </section>

      {/* Key Areas of Focus */}
      <section className="py-16 flex-grow">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center">Key Areas of Focus</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {areas.map((area, index) => (
              <MagicCard key={index} className={activeArea === index ? 'ring-2 ring-green-500' : ''}>
                <h3 className="text-xl font-semibold mb-4">{area.title}</h3>
                <AnimatePresence>
                  {activeArea === index && (
                    <motion.p
                      className="text-gray-600"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                    >
                      {area.description}
                    </motion.p>
                  )}
                </AnimatePresence>
              </MagicCard>
            ))}
          </div>
        </div>
      </section>

      {/* Get Involved Section */}
      <section className="bg-gray-100 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-8 text-center">Get Involved</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: "Volunteer with Us",
                description: "Join our team as a volunteer to work directly on our projects, from organizing workshops to assisting in community outreach programs.",
              },
              {
                title: "Partner with Us",
                description: "Collaborate with us as a partner organization, sponsor, or community ally to expand our initiatives and reach more people in need.",
              },
              {
                title: "Skill-Based Volunteering",
                description: "Use your skills to contribute—whether it's in marketing, counselling, teaching, or administration. Your expertise can make a big difference.",
              },
              {
                title: "Become a Fundraiser",
                description: "Organize your own fundraising events to support our causes and involve your community in making a difference.",
              },
              {
                title: "Become a Donor",
                description: "Your contributions make a lasting impact. Support our mission by donating to our programs in mental health, child welfare, and women's empowerment.",
              },
            ].map((item, index) => (
              <MagicCard key={index}>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600 mb-4">{item.description}</p>
                <MagicButton className="w-full bg-green-600 text-white hover:bg-green-700">
                  <Link href="/get-involved">Learn More</Link>
                </MagicButton>
              </MagicCard>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">Frequently Asked Questions</h2>
          <MagicButton className="bg-green-600 text-white hover:bg-green-700">
            <Link href="/faq">View FAQs</Link>
          </MagicButton>
        </div>
      </section>

      {/* Footer */}
      {/* <footer className="bg-green-800 text-white py-8"> */}
        {/* <div className="container mx-auto px-4"> */}
          {/* <div className="grid md:grid-cols-2 gap-8"> */}
            {/* <div> */}
              {/* <h3 className="text-xl font-semibold mb-4">Contact Us</h3> */}
              {/* <p>Email: vikasalaya@gmail.com</p> */}
              {/* <p>Phone: 7204453790; 8088212774</p> */}
            {/* </div> */}
            {/* <div> */}
              {/* <h3 className="text-xl font-semibold mb-4">Our Locations</h3> */}
              {/* <p>Pradhan Khanta, Baliapur, Dhanbad</p> */}
              {/* <p>Ohana 857, KR Puram, Bangalore, 560049</p> */}
            {/* </div> */}
          {/* </div> */}
          {/* <div className="mt-8 text-center text-gray-400"> */}
            {/* <p>&copy; {new Date().getFullYear()} Vikasalaya Foundation. All rights reserved.</p> */}
          {/* </div> */}
        {/* </div> */}
      {/* </footer> */}
    </div>
  )
}

export default function Page() {
  return (
    <>
      <FloatingNavbar />
      <BlockPage />
    </>
  );
}