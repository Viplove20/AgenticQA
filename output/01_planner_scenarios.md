SCENARIO_ID: SCN-001
MODULE: Login
SCENARIO: Verify user can login with valid credentials

SCENARIO_ID: SCN-002
MODULE: Login
SCENARIO: Verify error message is displayed for invalid password

SCENARIO_ID: SCN-003
MODULE: Login
SCENARIO: Verify login fails when username field is empty

SCENARIO_ID: SCN-004
MODULE: Dashboard
SCENARIO: Verify user dashboard loads successfully after login

SCENARIO_ID: SCN-005
MODULE: Dashboard
SCENARIO: Verify user can search for products using search bar

SCENARIO_ID: SCN-006
MODULE: Dashboard
SCENARIO: Verify user can filter products by price range

SCENARIO_ID: SCN-007
MODULE: Dashboard
SCENARIO: Verify user can filter products by category

SCENARIO_ID: SCN-008
MODULE: Dashboard
SCENARIO: Verify user can view product details

SCENARIO_ID: SCN-009
MODULE: Dashboard
SCENARIO: Verify user can add product to cart

SCENARIO_ID: SCN-010
MODULE: Cart
SCENARIO: Verify that cart shows items added by user

SCENARIO_ID: SCN-011
MODULE: Cart
SCENARIO: Verify user can remove an item from the cart

SCENARIO_ID: SCN-012
MODULE: Cart
SCENARIO: Verify the total price is correctly calculated in the cart

SCENARIO_ID: SCN-013
MODULE: Cart
SCENARIO: Verify user can proceed to checkout from the cart

SCENARIO_ID: SCN-014
MODULE: Checkout
SCENARIO: Verify checkout page is displayed when proceeding from cart

SCENARIO_ID: SCN-015
MODULE: Checkout
SCENARIO: Verify error message is displayed for invalid billing address fields

SCENARIO_ID: SCN-016
MODULE: Checkout
SCENARIO: Verify user can successfully complete a payment

SCENARIO_ID: SCN-017
MODULE: Order Summary
SCENARIO: Verify order summary displays correct order details after payment

SCENARIO_ID: SCN-018
MODULE: Order History
SCENARIO: Verify user can view past orders in order history

SCENARIO_ID: SCN-019
MODULE: Order History
SCENARIO: Verify user can filter past orders by status

SCENARIO_ID: SCN-020
MODULE: Order History
SCENARIO: Verify error message is displayed when there are no orders to show

SCENARIO_ID: SCN-021
MODULE: Cart
SCENARIO: Verify empty cart state shows correct message and icon

SCENARIO_ID: SCN-022
MODULE: Dashboard
SCENARIO: Verify pagination works correctly for product listings

SCENARIO_ID: SCN-023
MODULE: Checkout
SCENARIO: Verify continue to payment button is disabled with invalid form

SCENARIO_ID: SCN-024
MODULE: Checkout
SCENARIO: Verify user is redirected back to cart when clicking "Back to Cart"