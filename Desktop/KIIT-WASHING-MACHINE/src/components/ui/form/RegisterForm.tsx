import { AnimatedButton } from "@/components/ui/animated-button";

<AnimatedButton
  type="submit"
  variant="primary"
  size="default"
  fullWidth
>
  Sign up &rarr;
</AnimatedButton>

<AnimatedButton
  type="button"
  variant="secondary"
  size="default"
  fullWidth
  onClick={() => {
    console.log("Google Sign In clicked");
  }}
>
  <IconBrandGoogle className="h-4 w-4" />
  <span>Sign up with KIIT Email</span>
</AnimatedButton> 