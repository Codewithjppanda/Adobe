'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
}

export default function AboutPage() {
  const [activeTab, setActiveTab] = useState('mission')

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <main className="container mx-auto px-4 py-16 flex-grow">
        <motion.h1 
          className="text-5xl font-bold text-center mb-16 text-green-800"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          About Vikasalaya Foundation
        </motion.h1>

        <section className="mb-24">
          <Tabs defaultValue="mission" className="w-full" onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="mission">Mission</TabsTrigger>
              <TabsTrigger value="vision">Vision</TabsTrigger>
              <TabsTrigger value="values">Core Values</TabsTrigger>
            </TabsList>
            <motion.div
              key={activeTab}
              initial="initial"
              animate="animate"
              variants={fadeIn}
            >
              <TabsContent value="mission">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-2xl text-green-700">Our Mission</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-lg leading-relaxed">To empower individuals and communities through holistic development initiatives that prioritize mental health, child welfare, and women's empowerment. Vikasalaya Foundation is committed to breaking barriers, fostering resilience, and creating sustainable change for a brighter, more inclusive future.</p>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="vision">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-2xl text-green-700">Our Vision</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-lg leading-relaxed">A world where every individual has access to the resources, support, and opportunities needed to thrive—regardless of social or economic barriers. We envision a future where mental health is openly supported, children grow up in nurturing environments, and women are empowered to lead and succeed in all aspects of life.</p>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="values">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-2xl text-green-700">Our Core Values</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="list-none space-y-4">
                      {[
                        { title: "Compassion", desc: "We believe in the power of empathy and kindness to drive change. Our programs are designed to meet the unique needs of each community with understanding and care." },
                        { title: "Inclusivity", desc: "We are committed to creating spaces where all voices are heard and respected. Our work embraces diversity and ensures equal opportunities for everyone, regardless of background." },
                        { title: "Empowerment", desc: "We aim to build self-reliance and confidence, enabling individuals to take charge of their own lives and create positive change within their communities." },
                        { title: "Integrity", desc: "We operate with transparency, accountability, and ethical practices. Every action is guided by honesty and a commitment to uphold trust within the communities we serve." },
                        { title: "Sustainability", desc: "Our approach is rooted in long-term impact, creating programs that promote sustainable growth and development to benefit future generations." }
                      ].map((value, index) => (
                        <li key={index} className="flex items-start">
                          <span className="inline-block w-4 h-4 mr-2 mt-1 bg-green-500 rounded-full"></span>
                          <div>
                            <h3 className="font-semibold text-lg">{value.title}</h3>
                            <p className="text-gray-600">{value.desc}</p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </TabsContent>
            </motion.div>
          </Tabs>
        </section>

        <motion.section className="mb-24" {...fadeIn}>
          <h2 className="text-4xl font-semibold mb-12 text-green-700 text-center">Our Team</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: "Vikash Kumar Paul", role: "Founder & CEO" },
              { name: "Priyadarshni Rawal", role: "Program Director" },
              { name: "Prerna Maheshwari", role: "Community Outreach Manager" }
            ].map((member, index) => (
              <motion.div key={member.name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: index * 0.2 }}>
                <Card className="overflow-hidden">
                  <CardContent className="flex flex-col items-center pt-6">
                    <Avatar className="w-32 h-32 mb-4">
                      <AvatarImage src={`https://api.dicebear.com/6.x/initials/svg?seed=${member.name}`} />
                      <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                    </Avatar>
                    <h3 className="text-2xl font-semibold">{member.name}</h3>
                    <p className="text-gray-600">{member.role}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.section>

        <motion.section className="mb-24" {...fadeIn}>
          <h2 className="text-4xl font-semibold mb-12 text-green-700 text-center">Our Programs</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              "Mental Health Awareness",
              "Child Development and Education",
              "Women Empowerment and Skill Development"
            ].map((program, index) => (
              <motion.div key={program} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: index * 0.2 }}>
                <Card className="h-full flex flex-col">
                  <CardHeader>
                    <CardTitle className="text-xl text-green-700">{program}</CardTitle>
                  </CardHeader>
                  <CardContent className="flex-grow">
                    <p className="text-gray-600 mb-4">Empowering communities through targeted initiatives and support.</p>
                    <Button className="mt-auto w-full">Learn More</Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.section>

        <motion.section {...fadeIn}>
          <h2 className="text-4xl font-semibold mb-12 text-green-700 text-center">Resources & Events</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl text-green-700">Resources</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2 mb-6">
                  <li>Annual report</li>
                  <li>Policy documents</li>
                </ul>
                <Button className="w-full">Access Resources</Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl text-green-700">Upcoming Events</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-6">Join us for workshops, seminars, and community events. Stay updated on our latest initiatives and how you can contribute to positive change.</p>
                <Button className="w-full">View Events Calendar</Button>
              </CardContent>
            </Card>
          </div>
        </motion.section>
      </main>

      <footer className="bg-green-800 text-white py-8 mt-auto">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold mb-4">Contact Us</h3>
              <p>Email: vikasalaya@gmail.com</p>
              <p>Phone: 7204453790; 8088212774</p>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-4">Our Locations</h3>
              <p>Pradhan Khanta, Baliapur, Dhanbad</p>
              <p>Ohana 857, KR Puram, Bangalore, 560049</p>
            </div>
          </div>
          <div className="mt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} Vikasalaya Foundation. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}