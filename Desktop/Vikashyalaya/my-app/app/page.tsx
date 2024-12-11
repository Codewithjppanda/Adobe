import { BlockPage } from "@/components/page"
import AboutPage from "@/components/about"
import { FloatingNav } from "@/components/FloatingNav"


export default function Page() {
  return (
    <div>
      <FloatingNav 
        navItems={[
          { name: 'Home', link: '/' },
          { name: 'About', link: '/about' },
          { name: 'Get Involved', link: '/get-involved' },
          { name: 'Donate', link: '/donate' },
          { name: 'FAQs', link: '/faq' }
        ]}
      />
      <BlockPage />
      <AboutPage />

    </div>
  )
}