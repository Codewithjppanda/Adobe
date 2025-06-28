import { AnimatedButton } from "@/components/ui/animated-button";

// ... replace the reset password button with:
<AnimatedButton
  onClick={handleResetPassword}
  disabled={isLoading}
  variant="primary"
  size="default"
  fullWidth
>
  {isLoading ? "Sending..." : "Send Reset Instructions"}
</AnimatedButton>

// ... replace the return to login button with:
<AnimatedButton
  onClick={() => router.push('/verify-password')}
  variant="outline"
  size="sm"
>
  Return to login
</AnimatedButton> 