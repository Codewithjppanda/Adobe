import { AnimatedButton } from "@/components/ui/animated-button";

// ... inside the return statement, replace the button with:
<AnimatedButton
  onClick={handleGoogleSignIn}
  disabled={isLoading || status === "loading"}
  variant="primary"
  size="lg"
  fullWidth
>
  <IconBrandGoogle className="h-5 w-5" />
  {isLoading || status === "loading" ? "Signing in..." : "Sign in with KIIT Email"}
</AnimatedButton> 