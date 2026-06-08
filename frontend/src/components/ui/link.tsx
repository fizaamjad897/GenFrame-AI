// /**
//  * TODO: Update this component to use your client-side framework's link
//  * component. We've provided examples of how to do this for Next.js, Remix, and
//  * Inertia.js in the Catalyst documentation:
//  *
//  * https://catalyst.tailwindui.com/docs#client-side-router-integration
//  */

// import * as Headless from "@headlessui/react";
// import React, { forwardRef } from "react";

// export const Link = forwardRef(function Link(
//   props: { href: string } & React.ComponentPropsWithoutRef<"a">,
//   ref: React.ForwardedRef<HTMLAnchorElement>,
// ) {
//   return (
//     <Headless.DataInteractive>
//       <a {...props} ref={ref} />
//     </Headless.DataInteractive>
//   );
// });

import React, { forwardRef } from "react";
import NextLink from "next/link";

type Props = { href: string } & React.ComponentPropsWithoutRef<"a">;

export const Link = forwardRef<HTMLAnchorElement, Props>(function Link(
  { href, children, ...props },
  ref,
) {
  const isExternal =
    typeof href === "string" &&
    (href.startsWith("http") ||
      href.startsWith("mailto:") ||
      href.startsWith("tel:"));

  if (isExternal) {
    // External links use normal <a>
    return (
      <a
        href={href}
        ref={ref}
        {...props}
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    );
  }

  // Internal links use Next.js Link directly (no legacyBehavior, no nested <a>)
  return (
    <NextLink href={href} {...props} ref={ref}>
      {children}
    </NextLink>
  );
});
